"""Dependencies for Messaging endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.messaging.use_cases.queue_message import QueueMessageUseCase
from app.infrastructure.db.repositories.contacts import ContactRepository
from app.infrastructure.db.repositories.identity import TenantRepository
from app.infrastructure.db.repositories.messaging import OutboxRepository
from app.infrastructure.db.session import get_session


async def get_queue_message_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QueueMessageUseCase:
    """Provide QueueMessageUseCase with dependencies."""
    outbox_repo = OutboxRepository(session)
    contact_repo = ContactRepository(session)
    tenant_repo = TenantRepository(session)
    return QueueMessageUseCase(
        outbox_repository=outbox_repo,
        contact_repository=contact_repo,
        tenant_repository=tenant_repo,
    )


async def get_outbox_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OutboxRepository:
    """Provide OutboxRepository for list operations."""
    return OutboxRepository(session)
