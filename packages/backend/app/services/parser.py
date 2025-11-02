from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from io import BytesIO
from typing import Dict, List, Optional

import mailparser
from loguru import logger

try:
    import extract_msg  # type: ignore
except Exception as exc:  # pragma: no cover - library import guard
    extract_msg = None
    logger.warning("extract_msg is not available: %s", exc)


URL_PATTERN = re.compile(
    r"((?:https?|ftp)://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+)",
    re.IGNORECASE,
)


@dataclass
class ParsedAttachment:
    filename: str
    content_type: str
    payload: bytes
    size: int


@dataclass
class ParsedEmail:
    subject: Optional[str]
    from_address: Optional[str]
    to_addresses: List[str]
    cc_addresses: List[str]
    date: datetime
    text_body: str
    html_body: Optional[str]
    headers: Dict[str, str]
    attachments: List[ParsedAttachment]
    urls: List[str]


class EmailParser:
    """Parse inbound EML/MSG files into a normalized shape."""

    def parse(self, file_bytes: bytes, filename: str) -> ParsedEmail:
        if filename.lower().endswith(".msg"):
            return self._parse_msg(file_bytes)
        return self._parse_eml(file_bytes)

    def _parse_eml(self, file_bytes: bytes) -> ParsedEmail:
        parser = mailparser.parse_from_bytes(file_bytes)
        subject = parser.subject
        from_address = parser.from_[0][1] if parser.from_ else None
        to_addresses = [item[1] for item in parser.to] if parser.to else []
        cc_addresses = [item[1] for item in parser.cc] if parser.cc else []
        date = parser.date or datetime.now(timezone.utc)

        text_body = "\n\n".join(parser.text_plain) if parser.text_plain else ""
        html_body = "\n".join(parser.text_html) if parser.text_html else None
        headers = {key: value for key, value in parser.headers.items()}  # type: ignore[arg-type]

        attachments: List[ParsedAttachment] = []
        for attachment in parser.attachments:
            filename = attachment.get("filename") or "attachment.bin"
            content_type = attachment.get("mail_content_type") or "application/octet-stream"
            payload = attachment.get("binary") or attachment.get("payload")
            payload_bytes: bytes
            if isinstance(payload, bytes):
                payload_bytes = payload
            elif isinstance(payload, bytearray):
                payload_bytes = bytes(payload)
            elif isinstance(payload, str):
                try:
                    payload_bytes = base64.b64decode(payload, validate=False)
                except Exception:  # pragma: no cover - fallback
                    payload_bytes = payload.encode()
            else:
                payload_bytes = b""
            attachments.append(
                ParsedAttachment(
                    filename=filename,
                    content_type=content_type,
                    payload=bytes(payload_bytes),
                    size=len(payload_bytes),
                )
            )

        urls = sorted(set(parser.urls or []))
        if not urls:
            urls = self._extract_urls_from_text(text_body)

        return ParsedEmail(
            subject=subject,
            from_address=from_address,
            to_addresses=to_addresses,
            cc_addresses=cc_addresses,
            date=date if isinstance(date, datetime) else datetime.now(timezone.utc),
            text_body=text_body,
            html_body=html_body,
            headers=headers,
            attachments=attachments,
            urls=urls,
        )

    def _parse_msg(self, file_bytes: bytes) -> ParsedEmail:
        if extract_msg is None:
            raise RuntimeError("extract_msg library is not available")

        message = extract_msg.Message(stream=BytesIO(file_bytes))
        message.process()

        subject = message.subject
        from_address = message.sender
        to_addresses = message.to if isinstance(message.to, list) else [message.to] if message.to else []
        cc_addresses = message.cc if isinstance(message.cc, list) else [message.cc] if message.cc else []

        text_body = message.body or ""
        html_body = getattr(message, "htmlBody", None)

        raw_headers = message.header or {}
        headers: Dict[str, str] = {}
        if isinstance(raw_headers, dict):
            headers = {str(k): str(v) for k, v in raw_headers.items()}
        elif isinstance(raw_headers, str):  # pragma: no cover - rarely triggered
            for line in raw_headers.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip()] = value.strip()

        attachments: List[ParsedAttachment] = []
        for attachment in message.attachments:
            filename = attachment.longFilename or attachment.shortFilename or "attachment.bin"
            data = attachment.data or b""
            content_type = attachment.mimeType or "application/octet-stream"
            if not isinstance(data, (bytes, bytearray)):
                data = bytes(data)
            attachments.append(
                ParsedAttachment(
                    filename=filename,
                    content_type=content_type,
                    payload=bytes(data),
                    size=len(data),
                )
            )

        urls = self._extract_urls_from_text(text_body)
        if html_body:
            urls.extend(self._extract_urls_from_text(html_body))
        urls = sorted(set(urls))

        date_header = headers.get("Date") or message.date
        if isinstance(date_header, datetime):
            message_date = date_header
        else:
            try:
                message_date = parsedate_to_datetime(date_header) if date_header else datetime.now(timezone.utc)
            except Exception:
                message_date = datetime.now(timezone.utc)

        return ParsedEmail(
            subject=subject,
            from_address=from_address,
            to_addresses=[addr for addr in to_addresses if addr],
            cc_addresses=[addr for addr in cc_addresses if addr],
            date=message_date,
            text_body=text_body,
            html_body=html_body,
            headers=headers,
            attachments=attachments,
            urls=urls,
        )

    @staticmethod
    def _extract_urls_from_text(text: Optional[str]) -> List[str]:
        if not text:
            return []
        return URL_PATTERN.findall(text)

