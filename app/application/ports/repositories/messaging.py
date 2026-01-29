"""Repository ports for Messaging bounded context."""

from abc import ABC, abstractmethod

from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.messaging.entities.outbox_item import MessageOutboxItem
from app.domain.messaging.value_objects.outbox_item_id import OutboxItemId


class OutboxRepositoryPort(ABC):
    """Port for MessageOutboxItem persistence operations."""

    @abstractmethod
    async def get_by_id(self, item_id: OutboxItemId) -> MessageOutboxItem | None:
        """Retrieve an outbox item by its ID."""
        ...

    @abstractmethod
    async def save(self, item: MessageOutboxItem) -> MessageOutboxItem:
        """Persist an outbox item (create or update)."""
        ...

    @abstractmethod
    async def get_pending(
        self, tenant_id: TenantId | None = None, limit: int = 100
    ) -> list[MessageOutboxItem]:
        """Get pending items ready for delivery."""
        ...

    @abstractmethod
    async def exists_by_idempotency_key(
        self, tenant_id: TenantId, idempotency_key: str
    ) -> bool:
        """Check if an item with given idempotency key exists."""
        ...
