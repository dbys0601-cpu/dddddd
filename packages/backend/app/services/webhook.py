from __future__ import annotations

from typing import Optional

import httpx
import orjson
from loguru import logger

from ..models.schemas import TriageReport
from ..utils.security import compute_hmac_signature


class ReportWebhookDispatcher:
    def __init__(self, url: Optional[str], secret: Optional[str], timeout: float) -> None:
        self.url = url
        self.secret = secret
        self._client = httpx.AsyncClient(timeout=timeout)

    async def send(self, report: TriageReport) -> None:
        if not self.url:
            return
        body = orjson.dumps(report.model_dump(mode="json"))
        headers = {"Content-Type": "application/json"}
        if self.secret:
            headers["X-REPORT-SIGNATURE"] = compute_hmac_signature(body, self.secret)
        try:
            response = await self._client.post(self.url, content=body, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - network errors
            logger.warning("Failed to push report: %s", exc)

    async def close(self) -> None:
        await self._client.aclose()

