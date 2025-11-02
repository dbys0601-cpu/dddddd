import re
from typing import Iterable, List, Sequence, Set

from ..models.schemas import IOCMatches

DOMAIN_PATTERN = re.compile(r"\b([a-z0-9][-a-z0-9]{0,62}\.)+[a-z]{2,63}\b", re.IGNORECASE)
IP_PATTERN = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)(?:\.|$)){4}\b")
URL_PATTERN = re.compile(
    r"((?:https?|ftp)://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+)",
    re.IGNORECASE,
)
HASH_PATTERN = re.compile(r"\b[a-fA-F0-9]{32,64}\b")


def _collect_matches(pattern: re.Pattern[str], texts: Sequence[str]) -> Set[str]:
    values: Set[str] = set()
    for text in texts:
        if not text:
            continue
        for match in pattern.findall(text):
            if isinstance(match, tuple):
                values.add(match[0])
            else:
                values.add(match)
    return values


def extract_iocs(*texts: Iterable[str]) -> IOCMatches:
    flat_texts: List[str] = []
    for segment in texts:
        if isinstance(segment, (list, tuple, set)):
            flat_texts.extend([str(item) for item in segment])
        else:
            flat_texts.append(str(segment))

    domains = _collect_matches(DOMAIN_PATTERN, flat_texts)
    urls = _collect_matches(URL_PATTERN, flat_texts)
    ips = _collect_matches(IP_PATTERN, flat_texts)
    hashes = _collect_matches(HASH_PATTERN, flat_texts)

    # Remove overlaps (domains that are part of URLs)
    for url in list(urls):
        try:
            host = re.sub(r"^https?://", "", url, flags=re.IGNORECASE).split("/")[0]
            if host in domains:
                domains.discard(host)
        except Exception:  # pragma: no cover - defensive
            continue

    return IOCMatches(
        domains=sorted(domains),
        urls=sorted(urls),
        ips=sorted(ips),
        hashes=sorted(hashes),
    )

