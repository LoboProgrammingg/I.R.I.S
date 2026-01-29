"""Redis client management."""

from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends

from app.config.settings import Settings, get_settings


def create_redis_client(settings: Settings) -> redis.Redis:
    """Create async Redis client."""
    return redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


async def get_redis_health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> bool:
    """Check Redis connectivity."""
    try:
        client = create_redis_client(settings)
        await client.ping()
        await client.aclose()
        return True
    except Exception:
        return False
