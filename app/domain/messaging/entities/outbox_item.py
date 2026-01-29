"""MessageOutboxItem aggregate root."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.domain.contacts.value_objects.contact_id import ContactId
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.messaging.value_objects.delivery_status import DeliveryStatus
from app.domain.messaging.value_objects.message_type import MessageType
from app.domain.messaging.value_objects.outbox_item_id import OutboxItemId


@dataclass
class MessageOutboxItem:
    """MessageOutboxItem aggregate root.

    Represents a message queued for delivery via the Outbox Pattern.

    Invariants:
    - Item belongs to exactly one tenant
    - Idempotency key must be unique per tenant
    - Attempt count incremented safely
    - SENT items are immutable
    """

    id: OutboxItemId
    tenant_id: TenantId
    contact_id: ContactId
    message_type: MessageType
    status: DeliveryStatus
    payload: dict[str, Any]
    idempotency_key: str
    attempt_count: int = 0
    last_error: str | None = None
    scheduled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate outbox item invariants."""
        if not self.idempotency_key or not self.idempotency_key.strip():
            raise ValueError("Idempotency key must not be empty")
        if self.attempt_count < 0:
            raise ValueError("Attempt count cannot be negative")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        contact_id: ContactId,
        message_type: MessageType,
        payload: dict[str, Any],
        idempotency_key: str,
        scheduled_at: datetime | None = None,
        item_id: OutboxItemId | None = None,
    ) -> "MessageOutboxItem":
        """Factory method to create a new outbox item."""
        return cls(
            id=item_id or OutboxItemId.generate(),
            tenant_id=tenant_id,
            contact_id=contact_id,
            message_type=message_type,
            status=DeliveryStatus.PENDING,
            payload=payload,
            idempotency_key=idempotency_key.strip(),
            scheduled_at=scheduled_at or datetime.now(timezone.utc),
        )

    def mark_as_sent(self) -> None:
        """Mark item as successfully sent."""
        self.status = DeliveryStatus.SENT
        self.sent_at = datetime.now(timezone.utc)
        self._touch()

    def mark_as_failed(self, error: str) -> None:
        """Mark item as permanently failed."""
        self.status = DeliveryStatus.FAILED
        self.last_error = error
        self._touch()

    def mark_for_retry(self, error: str) -> None:
        """Mark item for retry after failure."""
        self.status = DeliveryStatus.RETRYING
        self.attempt_count += 1
        self.last_error = error
        self._touch()

    def increment_attempt(self) -> None:
        """Increment attempt counter."""
        self.attempt_count += 1
        self._touch()

    def is_sent(self) -> bool:
        """Check if item was sent."""
        return self.status == DeliveryStatus.SENT

    def is_failed(self) -> bool:
        """Check if item failed."""
        return self.status == DeliveryStatus.FAILED

    def is_retriable(self) -> bool:
        """Check if item can be retried."""
        return self.status.is_retriable()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MessageOutboxItem):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
