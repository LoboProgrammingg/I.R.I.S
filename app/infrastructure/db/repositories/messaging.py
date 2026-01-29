"""Repository implementation for Messaging bounded context."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories.messaging import OutboxRepositoryPort
from app.domain.contacts.value_objects.contact_id import ContactId
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.messaging.entities.outbox_item import MessageOutboxItem
from app.domain.messaging.value_objects.delivery_status import DeliveryStatus
from app.domain.messaging.value_objects.message_type import MessageType
from app.domain.messaging.value_objects.outbox_item_id import OutboxItemId
from app.infrastructure.db.models.messaging import MessageOutboxModel


class OutboxRepository(OutboxRepositoryPort):
    """SQLAlchemy implementation of OutboxRepositoryPort."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, item_id: OutboxItemId) -> MessageOutboxItem | None:
        """Retrieve an outbox item by its ID."""
        result = await self._session.execute(
            select(MessageOutboxModel).where(MessageOutboxModel.id == item_id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def save(self, item: MessageOutboxItem) -> MessageOutboxItem:
        """Persist an outbox item (create or update)."""
        existing = await self._session.get(MessageOutboxModel, item.id.value)

        if existing is None:
            model = self._to_model(item)
            self._session.add(model)
        else:
            existing.status = item.status.value
            existing.attempt_count = item.attempt_count
            existing.last_error = item.last_error
            existing.sent_at = item.sent_at
            existing.updated_at = item.updated_at
            model = existing

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_pending(
        self, tenant_id: TenantId | None = None, limit: int = 100
    ) -> list[MessageOutboxItem]:
        """Get pending items ready for delivery."""
        now = datetime.now(timezone.utc)
        query = select(MessageOutboxModel).where(
            MessageOutboxModel.status.in_(["pending", "retrying"]),
            MessageOutboxModel.scheduled_at <= now,
        )

        if tenant_id is not None:
            query = query.where(MessageOutboxModel.tenant_id == tenant_id.value)

        query = query.order_by(MessageOutboxModel.scheduled_at).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def exists_by_idempotency_key(
        self, tenant_id: TenantId, idempotency_key: str
    ) -> bool:
        """Check if an item with given idempotency key exists."""
        result = await self._session.execute(
            select(MessageOutboxModel.id).where(
                MessageOutboxModel.tenant_id == tenant_id.value,
                MessageOutboxModel.idempotency_key == idempotency_key,
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_domain(model: MessageOutboxModel) -> MessageOutboxItem:
        """Map SQLAlchemy model to domain entity."""
        return MessageOutboxItem(
            id=OutboxItemId(value=model.id),
            tenant_id=TenantId(value=model.tenant_id),
            contact_id=ContactId(value=model.contact_id),
            message_type=MessageType(model.message_type),
            status=DeliveryStatus(model.status),
            payload=model.payload,
            idempotency_key=model.idempotency_key,
            attempt_count=model.attempt_count,
            last_error=model.last_error,
            scheduled_at=model.scheduled_at,
            sent_at=model.sent_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(item: MessageOutboxItem) -> MessageOutboxModel:
        """Map domain entity to SQLAlchemy model."""
        return MessageOutboxModel(
            id=item.id.value,
            tenant_id=item.tenant_id.value,
            contact_id=item.contact_id.value,
            message_type=item.message_type.value,
            status=item.status.value,
            payload=item.payload,
            idempotency_key=item.idempotency_key,
            attempt_count=item.attempt_count,
            last_error=item.last_error,
            scheduled_at=item.scheduled_at,
            sent_at=item.sent_at,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
