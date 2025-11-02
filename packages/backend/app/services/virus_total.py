from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

from ..models.schemas import VirusTotalResult


class MockVirusTotalClient:
    """Deterministic mock to emulate VirusTotal verdicts during development."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key

    async def lookup(self, sha256: str) -> VirusTotalResult:
        # Sleep a tiny bit to mimic network latency without slowing tests too much
        await asyncio.sleep(0)
        seed = int(sha256[:4], 16)
        total_engines = 70
        malicious_engines = seed % 10
        return VirusTotalResult(
            malicious_engines=malicious_engines,
            total_engines=total_engines,
            scan_id=f"mock-{sha256[:12]}",
            scanned_at=datetime.now(timezone.utc),
            permalink=None,
        )

