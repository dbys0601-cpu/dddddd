from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TRIAGE_",
        extra="ignore",
    )

    app_name: str = "CatchProbe Email Triage"
    environment: str = Field("local", description="Deployment environment name")

    api_keys: List[str] = Field(
        default_factory=lambda: ["local-api-key"],
        description="Allowed API keys for direct ingest",
    )
    catchprobe_api_keys: List[str] = Field(
        default_factory=lambda: ["local-catchprobe-key"],
        description="Allowed API keys for CatchProbe ingress",
    )

    report_base_dir: Path = Field(
        default=Path("storage"),
        description="Base directory to persist reports and artifacts",
    )
    max_file_size_mb: int = Field(20, ge=1, le=100)
    request_timeout_seconds: float = Field(10.0, ge=1.0, le=60.0)
    url_head_timeout_seconds: float = Field(5.0, ge=1.0, le=30.0)

    yara_rules_dir: Path = Field(
        default=Path(__file__).parent / "static_rules",
        description="Directory containing YARA rule files",
    )

    virus_total_mock: bool = Field(
        default=True,
        description="When true, skip real VirusTotal queries and emit deterministic mock responses",
    )

    report_webhook_url: Optional[HttpUrl] = Field(
        default=None,
        description="Optional URL to push reports via POST",
    )
    report_webhook_secret: Optional[str] = Field(
        default=None,
        description="Shared secret for report push HMAC signatures",
    )

    enable_cors: bool = Field(True, description="Enable CORS middleware")
    cors_origins: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS origins",
    )

    sentry_dsn: Optional[str] = Field(default=None, description="Optional Sentry DSN")

    @field_validator("api_keys", "catchprobe_api_keys", "cors_origins", mode="before")
    @classmethod
    def _split_csv(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def max_file_size_bytes(self) -> int:
        return int(self.max_file_size_mb * 1024 * 1024)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.report_base_dir.mkdir(parents=True, exist_ok=True)
    (settings.report_base_dir / "artifacts").mkdir(parents=True, exist_ok=True)
    (settings.report_base_dir / "reports").mkdir(parents=True, exist_ok=True)
    return settings

