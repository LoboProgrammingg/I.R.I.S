"""Messaging bounded context - domain layer."""

from app.domain.messaging.entities.outbox_item import MessageOutboxItem
from app.domain.messaging.exceptions import (
    ContactOptedOutError,
    DuplicateMessageError,
    MessageNotFoundError,
    MessagingDomainError,
)
from app.domain.messaging.value_objects.delivery_status import DeliveryStatus
from app.domain.messaging.value_objects.message_type import MessageType
from app.domain.messaging.value_objects.outbox_item_id import OutboxItemId

__all__ = [
    "MessageOutboxItem",
    "OutboxItemId",
    "MessageType",
    "DeliveryStatus",
    "MessagingDomainError",
    "MessageNotFoundError",
    "DuplicateMessageError",
    "ContactOptedOutError",
]
