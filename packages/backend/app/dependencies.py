from functools import lru_cache

from fastapi import Depends

from .config import Settings, get_settings
from .services.storage import ArtifactStore
from .services.triage import TriageService
from .services.url_tools import URLExpander
from .services.virus_total import MockVirusTotalClient
from .services.webhook import ReportWebhookDispatcher
from .services.yara_scanner import YaraScanner


@lru_cache(maxsize=1)
def get_artifact_store() -> ArtifactStore:
    settings = get_settings()
    return ArtifactStore(settings.report_base_dir)


@lru_cache(maxsize=1)
def get_yara_scanner() -> YaraScanner:
    settings = get_settings()
    return YaraScanner(settings.yara_rules_dir)


@lru_cache(maxsize=1)
def get_vt_client() -> MockVirusTotalClient:
    return MockVirusTotalClient()


@lru_cache(maxsize=1)
def get_url_expander() -> URLExpander:
    settings = get_settings()
    return URLExpander(timeout=settings.url_head_timeout_seconds)


@lru_cache(maxsize=1)
def get_webhook_dispatcher() -> ReportWebhookDispatcher:
    settings = get_settings()
    return ReportWebhookDispatcher(
        url=settings.report_webhook_url,
        secret=settings.report_webhook_secret,
        timeout=settings.request_timeout_seconds,
    )


def get_triage_service(
    settings: Settings = Depends(get_settings),
    store: ArtifactStore = Depends(get_artifact_store),
    yara_scanner: YaraScanner = Depends(get_yara_scanner),
    vt_client: MockVirusTotalClient = Depends(get_vt_client),
    url_expander: URLExpander = Depends(get_url_expander),
    webhook_dispatcher: ReportWebhookDispatcher = Depends(get_webhook_dispatcher),
) -> TriageService:
    return TriageService(
        settings=settings,
        store=store,
        yara_scanner=yara_scanner,
        vt_client=vt_client,
        url_expander=url_expander,
        webhook_dispatcher=webhook_dispatcher,
    )

