"""Pydantic schemas for Billing HTTP endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateBoletoRequest(BaseModel):
    """Request schema for creating a boleto."""

    contact_id: str = Field(..., description="Contact UUID")
    amount_cents: int = Field(..., gt=0, description="Amount in cents")
    due_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Due date in ISO format (YYYY-MM-DD)",
    )
    idempotency_key: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique key to prevent duplicate boletos",
    )
    confirmed: bool = Field(
        default=False,
        description="Explicit confirmation for monetary action",
    )


class CancelBoletoRequest(BaseModel):
    """Request schema for cancelling a boleto."""

    confirmed: bool = Field(
        default=False,
        description="Explicit confirmation for monetary action",
    )


class BoletoResponse(BaseModel):
    """Response schema for boleto data."""

    id: str = Field(..., description="Boleto UUID")
    tenant_id: str = Field(..., description="Tenant UUID")
    contact_id: str = Field(..., description="Contact UUID")
    amount_cents: int = Field(..., description="Amount in cents")
    currency: str = Field(..., description="Currency code")
    due_date: str = Field(..., description="Due date (YYYY-MM-DD)")
    status: str = Field(..., description="Boleto status")
    idempotency_key: str = Field(..., description="Idempotency key")
    provider_reference: str | None = Field(default=None, description="Provider reference")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}
