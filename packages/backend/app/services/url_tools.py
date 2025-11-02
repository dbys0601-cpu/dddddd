from __future__ import annotations

from typing import List
from urllib.parse import urlparse

import httpx

from ..models.schemas import URLInsight


SUSPICIOUS_TLDS = {"zip", "mov", "country", "link", "xyz", "ru"}


class URLExpander:
    def __init__(self, timeout: float) -> None:
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            headers={"User-Agent": "CatchProbe-Triage/1.0"},
        )

    async def expand_many(self, urls: List[str]) -> List[URLInsight]:
        insights: List[URLInsight] = []
        for url in urls:
            insights.append(await self.expand(url))
        return insights

    async def expand(self, url: str) -> URLInsight:
        parsed = urlparse(url)
        domain = parsed.netloc
        risk_hint = self._risk_from_domain(domain)
        try:
            response = await self._client.head(url)
            expanded_url = str(response.url)
            status = response.status_code
        except httpx.HTTPError:
            expanded_url = None
            status = None
        if expanded_url and expanded_url != url:
            parsed = urlparse(expanded_url)
            domain = parsed.netloc or domain
            risk_hint = risk_hint or self._risk_from_domain(domain)
        return URLInsight(
            original=url,
            expanded=expanded_url,
            domain=domain,
            status_code=status,
            risk_hint=risk_hint,
        )

    async def close(self) -> None:
        await self._client.aclose()

    @staticmethod
    def _risk_from_domain(domain: str | None) -> str | None:
        if not domain:
            return None
        parts = domain.lower().split(".")
        if parts and parts[-1] in SUSPICIOUS_TLDS:
            return "y?ksek risk"
        if domain.endswith(".gov") or domain.endswith(".edu"):
            return "d???k risk"
        return None

