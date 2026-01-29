"""Messaging domain events.

These are definitions only - event publishing infrastructure comes later.
"""

from dataclasses import dataclass
from datetime import datetime

from app.domain.messaging.value_objects.message_type import MessageType
from app.domain.messaging.value_objects.outbox_item_id import OutboxItemId


@dataclass(frozen=True)
class MessageQueued:
    """Event raised when a new message is added to the outbox."""

    item_id: OutboxItemId
    tenant_id: str
    contact_id: str
    message_type: MessageType
    occurred_at: datetime


@dataclass(frozen=True)
class MessageSent:
    """Event raised when a message is delivered successfully."""

    item_id: OutboxItemId
    sent_at: datetime
    occurred_at: datetime


@dataclass(frozen=True)
class MessageFailed:
    """Event raised when message delivery fails permanently."""

    item_id: OutboxItemId
    error: str
    attempt_count: int
    occurred_at: datetime
