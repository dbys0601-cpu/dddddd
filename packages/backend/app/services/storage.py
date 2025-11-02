from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import orjson

from ..models.schemas import TriageReport


@dataclass
class ArtifactRecord:
    sha256: str
    filename: str
    content_type: str
    size: int
    path: Path


class ArtifactStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self.artifacts_dir = self.base_dir / "artifacts"
        self.reports_dir = self.base_dir / "reports"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self._report_cache: Dict[str, TriageReport] = {}
        self._lock = asyncio.Lock()

    async def save_artifact(
        self,
        sha256: str,
        data: bytes,
        filename: str,
        content_type: str,
    ) -> ArtifactRecord:
        async with self._lock:
            path = self.artifacts_dir / sha256
            if not path.exists():
                path.write_bytes(data)
            metadata_path = self.artifacts_dir / f"{sha256}.json"
            metadata = {
                "sha256": sha256,
                "filename": filename,
                "content_type": content_type,
                "size": len(data),
            }
            metadata_path.write_bytes(orjson.dumps(metadata))
        return ArtifactRecord(
            sha256=sha256,
            filename=filename,
            content_type=content_type,
            size=len(data),
            path=path,
        )

    async def get_artifact(self, sha256: str) -> Optional[ArtifactRecord]:
        path = self.artifacts_dir / sha256
        if not path.exists():
            return None
        metadata_path = self.artifacts_dir / f"{sha256}.json"
        if metadata_path.exists():
            metadata = orjson.loads(metadata_path.read_bytes())
            return ArtifactRecord(
                sha256=sha256,
                filename=metadata.get("filename", sha256),
                content_type=metadata.get("content_type", "application/octet-stream"),
                size=metadata.get("size", path.stat().st_size),
                path=path,
            )
        return ArtifactRecord(
            sha256=sha256,
            filename=sha256,
            content_type="application/octet-stream",
            size=path.stat().st_size,
            path=path,
        )

    async def save_report(self, report: TriageReport) -> None:
        payload = orjson.dumps(report.model_dump(mode="json"))
        path = self.reports_dir / f"{report.ticket_id}.json"
        async with self._lock:
            path.write_bytes(payload)
            self._report_cache[report.ticket_id] = report

    async def get_report(self, ticket_id: str) -> Optional[TriageReport]:
        cached = self._report_cache.get(ticket_id)
        if cached:
            return cached
        path = self.reports_dir / f"{ticket_id}.json"
        if not path.exists():
            return None
        data = orjson.loads(path.read_bytes())
        report = TriageReport.model_validate(data)
        self._report_cache[ticket_id] = report
        return report

