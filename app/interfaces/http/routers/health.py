"""Health check endpoints."""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.infrastructure.db.session import get_db_health
from app.infrastructure.redis.client import get_redis_health

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


class ReadyResponse(BaseModel):
    """Readiness check response."""

    status: str
    database: str
    redis: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
)
async def health() -> HealthResponse:
    """Basic liveness check.

    Returns 200 if the application is running.
    """
    return HealthResponse(status="healthy")


@router.get(
    "/ready",
    response_model=ReadyResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
)
async def ready(
    db_healthy: bool = Depends(get_db_health),
    redis_healthy: bool = Depends(get_redis_health),
) -> ReadyResponse:
    """Readiness check verifying database and Redis connectivity.

    Returns 200 if all dependencies are accessible.
    """
    return ReadyResponse(
        status="ready" if (db_healthy and redis_healthy) else "degraded",
        database="connected" if db_healthy else "disconnected",
        redis="connected" if redis_healthy else "disconnected",
    )
