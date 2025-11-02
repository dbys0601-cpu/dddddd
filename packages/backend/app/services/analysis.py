from __future__ import annotations

import re
from typing import Dict, List, Sequence, Tuple

from ..models.schemas import (
    AttachmentReport,
    AuthenticationResults,
    MetadataPayload,
    TriageReport,
)


AUTH_PASS_VALUES = {"pass", "bestguesspass", "none"}
SUSPICIOUS_KEYWORDS = {
    "payment",
    "bitcoin",
    "password",
    "invoice",
    "?deme",
    "acil",
    "urgent",
    "fatura",
    "gift card",
    "mfa",
}


def evaluate_authentication(headers: Dict[str, str]) -> AuthenticationResults:
    header_val = headers.get("Authentication-Results", "")
    results = AuthenticationResults()

    def _extract(result_type: str) -> str | None:
        pattern = rf"{result_type}=([a-zA-Z]+)"
        match = re.search(pattern, header_val)
        if match:
            return match.group(1).lower()
        alt_header = headers.get(f"Received-{result_type.upper()}")
        if alt_header:
            token = alt_header.split(" ")[0].lower()
            return token
        return None

    results.spf = _extract("spf")
    results.dkim = _extract("dkim")
    results.dmarc = _extract("dmarc")

    return results


def _keyword_hits(texts: Sequence[str]) -> List[str]:
    hits: List[str] = []
    lowercase_text = " ".join(texts).lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in lowercase_text:
            hits.append(keyword)
    return hits


def calculate_score(
    authentication: AuthenticationResults,
    attachments: Sequence[AttachmentReport],
    url_count: int,
    metadata: MetadataPayload,
    keyword_hits: Sequence[str],
) -> Tuple[int, List[str]]:
    score = 10
    reasons: List[str] = []

    if authentication.spf and authentication.spf not in AUTH_PASS_VALUES:
        reasons.append("SPF do?rulamas? ba?ar?s?z")
        score += 20
    if authentication.dkim and authentication.dkim not in AUTH_PASS_VALUES:
        reasons.append("DKIM do?rulamas? ba?ar?s?z")
        score += 20
    if authentication.dmarc and authentication.dmarc not in AUTH_PASS_VALUES:
        reasons.append("DMARC politikas? uygunsuz")
        score += 20

    yara_hits = sum(len(att.yara_matches) for att in attachments)
    if yara_hits:
        reasons.append(f"YARA e?le?mesi ({yara_hits})")
        score += 25 + min(25, yara_hits * 5)

    vt_hits = sum(1 for att in attachments if att.vt_result and att.vt_result.malicious_engines >= 3)
    if vt_hits:
        reasons.append("VirusTotal ??pheli sonu?")
        score += 15

    if url_count > 0:
        reasons.append(f"Ekte {url_count} ba?lant? bulundu")
        score += min(20, url_count * 3)

    if keyword_hits:
        reasons.append("Riskli anahtar kelimeler: " + ", ".join(sorted(set(keyword_hits))))
        score += 15

    severity = metadata.severity_hint
    if severity == "high" or severity == "critical":
        reasons.append("Analist y?ksek risk i?areti verdi")
        score += 10
    elif severity == "medium":
        score += 5

    score = max(0, min(100, score))
    return score, reasons


def classify(score: int) -> str:
    if score >= 70:
        return "malicious"
    if score >= 40:
        return "suspicious"
    return "benign"


def summarize_report(report: TriageReport) -> str:
    attachment_names = ", ".join(att.filename for att in report.attachments) or "ek bulunmuyor"
    return (
        f"{report.ticket_id} bileti i?in triage sonu?lar?: "
        f"s?n?fland?rma {report.classification}, skor {report.triage_score}. "
        f"Ekler: {attachment_names}."
    )

