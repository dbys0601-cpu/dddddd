from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, model_validator


class MetadataPayload(BaseModel):
    ticket_id: Optional[str] = Field(default=None, description="CatchProbe ticket identifier")
    severity_hint: Optional[Literal["low", "medium", "high", "critical"]] = Field(
        default=None,
        description="Analyst provided severity hint",
    )
    notes: Optional[str] = Field(default=None, description="Additional analyst notes")

    @model_validator(mode="after")
    def _normalize(self):
        if self.severity_hint:
            normalized = self.severity_hint.lower()
            if normalized == "med":
                normalized = "medium"
            self.severity_hint = normalized
        return self


class VirusTotalResult(BaseModel):
    malicious_engines: int = 0
    total_engines: int = 0
    scan_id: str
    scanned_at: datetime
    permalink: Optional[HttpUrl] = None


class URLInsight(BaseModel):
    original: str
    expanded: Optional[str] = None
    domain: Optional[str] = None
    status_code: Optional[int] = None
    risk_hint: Optional[str] = None


class AttachmentReport(BaseModel):
    filename: str
    mime_type: Optional[str] = None
    size: int
    sha256: str
    yara_matches: List[str] = Field(default_factory=list)
    vt_result: Optional[VirusTotalResult] = None


class IOCMatches(BaseModel):
    domains: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    ips: List[str] = Field(default_factory=list)
    hashes: List[str] = Field(default_factory=list)


class AuthenticationResults(BaseModel):
    spf: Optional[str] = None
    dkim: Optional[str] = None
    dmarc: Optional[str] = None


class TriageReport(BaseModel):
    ticket_id: str
    triage_score: int
    classification: Literal["benign", "suspicious", "malicious"]
    reasons: List[str]
    summary: Optional[str] = None
    metadata: MetadataPayload
    subject: Optional[str] = None
    from_address: Optional[str] = None
    to_addresses: List[str] = Field(default_factory=list)
    cc_addresses: List[str] = Field(default_factory=list)
    received_at: datetime
    analysis_completed_at: datetime
    authentication: AuthenticationResults
    url_insights: List[URLInsight] = Field(default_factory=list)
    ioc_matches: IOCMatches = Field(default_factory=IOCMatches)
    attachments: List[AttachmentReport] = Field(default_factory=list)
    artifact_hashes: List[str] = Field(default_factory=list)
    raw_headers: Dict[str, str] = Field(default_factory=dict)
    hashes: Dict[str, str] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    status: Literal["accepted", "rejected", "error"]
    report: Optional[TriageReport] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str


class CatchProbeCallbackPayload(BaseModel):
    bucket: str
    key: str
    size: int
    etag: Optional[str] = None
    event_name: Optional[str] = None
    event_time: datetime
    metadata: Optional[Dict[str, str]] = None


class CatchProbeCallbackResponse(BaseModel):
    status: Literal["processed", "ignored"]
    message: Optional[str] = None

