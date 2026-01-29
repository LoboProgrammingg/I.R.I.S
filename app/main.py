"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.config.logging import configure_logging, get_logger
from app.config.settings import get_settings
from app.interfaces.http.routers import contacts, health, tenants


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager."""
    logger = get_logger("lifespan")
    settings = get_settings()

    logger.info(
        "application_starting",
        app_name=settings.app_name,
        environment=settings.app_env,
    )

    yield

    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Register routers
    app.include_router(health.router)
    app.include_router(tenants.router)
    app.include_router(contacts.router)

    return app


app = create_app()
