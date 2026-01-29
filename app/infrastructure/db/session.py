"""SQLAlchemy async session management."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text

from app.config.settings import Settings, get_settings


def create_engine(settings: Settings) -> create_async_engine:
    """Create async SQLAlchemy engine."""
    return create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def create_session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    """Create async session factory."""
    engine = create_engine(settings)
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_session(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    session_factory = create_session_factory(settings)
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_db_health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> bool:
    """Check database connectivity."""
    try:
        engine = create_engine(settings)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return True
    except Exception:
        return False
