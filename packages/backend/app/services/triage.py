from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from loguru import logger

from ..config import Settings
from ..models.schemas import (
    AttachmentReport,
    MetadataPayload,
    TriageReport,
)
from ..utils.hashing import md5_bytes, sha1_bytes, sha256_bytes
from ..utils.security import sanitize_filename
from .analysis import calculate_score, classify, evaluate_authentication, summarize_report, _keyword_hits
from .ioc import extract_iocs
from .parser import EmailParser
from .storage import ArtifactStore
from .url_tools import URLExpander
from .virus_total import MockVirusTotalClient
from .webhook import ReportWebhookDispatcher
from .yara_scanner import YaraScanner


class TriageService:
    def __init__(
        self,
        settings: Settings,
        store: ArtifactStore,
        yara_scanner: YaraScanner,
        vt_client: MockVirusTotalClient,
        url_expander: URLExpander,
        webhook_dispatcher: ReportWebhookDispatcher,
    ) -> None:
        self.settings = settings
        self.store = store
        self.yara_scanner = yara_scanner
        self.vt_client = vt_client
        self.url_expander = url_expander
        self.webhook_dispatcher = webhook_dispatcher
        self.parser = EmailParser()

    async def analyze(self, file_bytes: bytes, original_filename: str, metadata: MetadataPayload) -> TriageReport:
        sanitized_name = sanitize_filename(original_filename)
        parsed = self.parser.parse(file_bytes, sanitized_name)

        ticket_id = metadata.ticket_id or self._generate_ticket_id()
        metadata.ticket_id = ticket_id

        base_sha256 = sha256_bytes(file_bytes)
        base_record = await self.store.save_artifact(
            sha256=base_sha256,
            data=file_bytes,
            filename=sanitized_name,
            content_type="message/rfc822",
        )

        attachments: List[AttachmentReport] = []
        artifact_hashes = [base_record.sha256]
        for attachment in parsed.attachments:
            att_name = sanitize_filename(attachment.filename)
            att_hash = sha256_bytes(attachment.payload)
            yara_matches = self.yara_scanner.scan_bytes(attachment.payload)
            vt_result = await self.vt_client.lookup(att_hash) if attachment.payload else None
            artifact = await self.store.save_artifact(
                sha256=att_hash,
                data=attachment.payload,
                filename=att_name,
                content_type=attachment.content_type,
            )
            artifact_hashes.append(artifact.sha256)
            attachments.append(
                AttachmentReport(
                    filename=att_name,
                    mime_type=attachment.content_type,
                    size=attachment.size,
                    sha256=att_hash,
                    yara_matches=yara_matches,
                    vt_result=vt_result,
                )
            )

        authentication = evaluate_authentication(parsed.headers)
        url_insights = await self.url_expander.expand_many(parsed.urls[:10]) if parsed.urls else []

        keyword_hits = _keyword_hits([parsed.subject or "", parsed.text_body, parsed.html_body or ""])
        ioc_matches = extract_iocs(
            parsed.text_body,
            parsed.html_body or "",
            parsed.urls,
            list(parsed.headers.values()),
        )

        score, reasons = calculate_score(
            authentication=authentication,
            attachments=attachments,
            url_count=len(parsed.urls),
            metadata=metadata,
            keyword_hits=keyword_hits,
        )
        classification = classify(score)

        completion_time = datetime.now(timezone.utc)
        hashes = {
            "sha256": base_sha256,
            "sha1": sha1_bytes(file_bytes),
            "md5": md5_bytes(file_bytes),
        }

        report = TriageReport(
            ticket_id=ticket_id,
            triage_score=score,
            classification=classification,
            reasons=reasons,
            summary=None,
            metadata=metadata,
            subject=parsed.subject,
            from_address=parsed.from_address,
            to_addresses=parsed.to_addresses,
            cc_addresses=parsed.cc_addresses,
            received_at=parsed.date,
            analysis_completed_at=completion_time,
            authentication=authentication,
            url_insights=url_insights,
            ioc_matches=ioc_matches,
            attachments=attachments,
            artifact_hashes=artifact_hashes,
            raw_headers=parsed.headers,
            hashes=hashes,
        )
        report.summary = summarize_report(report)

        await self.store.save_report(report)
        await self._push_report(report)

        logger.info("Generated triage report for ticket {}", ticket_id)
        return report

    async def _push_report(self, report: TriageReport) -> None:
        try:
            await self.webhook_dispatcher.send(report)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Report webhook dispatch failed: %s", exc)

    @staticmethod
    def _generate_ticket_id() -> str:
        return f"CP-{uuid.uuid4().hex[:10].upper()}"

