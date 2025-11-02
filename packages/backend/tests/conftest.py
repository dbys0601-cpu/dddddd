import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.dependencies import (
    get_artifact_store,
    get_url_expander,
    get_vt_client,
    get_webhook_dispatcher,
    get_yara_scanner,
)
from app.main import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("TRIAGE_REPORT_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("TRIAGE_YARA_RULES_DIR", str(tmp_path / "rules"))
    monkeypatch.setenv("TRIAGE_API_KEYS", "local-api-key")
    monkeypatch.setenv("TRIAGE_CATCHPROBE_API_KEYS", "local-catchprobe-key")
    monkeypatch.setenv("TRIAGE_MAX_FILE_SIZE_MB", "2")

    get_settings.cache_clear()
    get_artifact_store.cache_clear()
    get_yara_scanner.cache_clear()
    get_vt_client.cache_clear()
    get_url_expander.cache_clear()
    get_webhook_dispatcher.cache_clear()

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

