from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger

from .api.routes import router
from .config import get_settings
from .dependencies import get_url_expander, get_webhook_dispatcher

try:  # pragma: no cover - optional dependency
    import sentry_sdk
except ImportError:  # pragma: no cover
    sentry_sdk = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    url_expander = get_url_expander()
    webhook_dispatcher = get_webhook_dispatcher()

    if settings.sentry_dsn and sentry_sdk:
        sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment)
        logger.info("Sentry initialized for environment {}", settings.environment)

    logger.info("Starting {} service", settings.app_name)
    try:
        yield
    finally:
        await url_expander.close()
        await webhook_dispatcher.close()
        logger.info("Shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.add_middleware(GZipMiddleware, minimum_size=1024)
    app.include_router(router)
    return app


app = create_app()

