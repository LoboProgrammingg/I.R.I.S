"""Pydantic schemas for Messaging HTTP endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QueueMessageRequest(BaseModel):
    """Request schema for queueing a message."""

    contact_id: str = Field(..., description="Contact UUID")
    message_type: str = Field(
        ...,
        pattern=r"^(boleto_send|reminder|notification)$",
        description="Message type",
    )
    payload: dict[str, Any] = Field(..., description="Message payload")
    idempotency_key: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique key to prevent duplicates",
    )
    scheduled_at: datetime | None = Field(
        default=None,
        description="When to deliver (default: now)",
    )


class OutboxItemResponse(BaseModel):
    """Response schema for outbox item."""

    id: str = Field(..., description="Item UUID")
    tenant_id: str = Field(..., description="Tenant UUID")
    contact_id: str = Field(..., description="Contact UUID")
    message_type: str = Field(..., description="Message type")
    status: str = Field(..., description="Delivery status")
    idempotency_key: str = Field(..., description="Idempotency key")
    attempt_count: int = Field(..., description="Delivery attempts")
    last_error: str | None = Field(default=None, description="Last error")
    scheduled_at: datetime = Field(..., description="Scheduled delivery time")
    sent_at: datetime | None = Field(default=None, description="Actual send time")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class OutboxListResponse(BaseModel):
    """Response schema for list of outbox items."""

    items: list[OutboxItemResponse] = Field(..., description="List of items")
    count: int = Field(..., description="Number of items returned")
