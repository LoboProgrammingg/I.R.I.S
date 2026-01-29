"""DTOs for Messaging use cases."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class QueueMessageInput:
    """Input for QueueMessage use case."""

    tenant_id: str
    contact_id: str
    message_type: str
    payload: dict[str, Any]
    idempotency_key: str
    scheduled_at: datetime | None = None


@dataclass(frozen=True)
class MarkMessageSentInput:
    """Input for MarkMessageSent use case."""

    item_id: str


@dataclass(frozen=True)
class MarkMessageFailedInput:
    """Input for MarkMessageFailed use case."""

    item_id: str
    error: str
    should_retry: bool = True
