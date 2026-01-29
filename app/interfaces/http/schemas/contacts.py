"""Pydantic schemas for Contacts HTTP endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateContactRequest(BaseModel):
    """Request schema for creating a contact."""

    phone_number: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Phone number in E.164 format",
        examples=["+5511999998888"],
    )
    name: str = Field(..., min_length=1, max_length=255, description="Contact name")
    email: str | None = Field(
        default=None,
        max_length=255,
        description="Optional email address",
    )


class UpdateContactRequest(BaseModel):
    """Request schema for updating a contact."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New contact name",
    )
    email: str | None = Field(
        default=None,
        max_length=255,
        description="New email address",
    )


class OptOutRequest(BaseModel):
    """Request schema for opt-out preference."""

    opt_out: bool = Field(
        default=True,
        description="True to opt out, False to opt in",
    )


class ContactResponse(BaseModel):
    """Response schema for contact data."""

    id: str = Field(..., description="Contact UUID")
    tenant_id: str = Field(..., description="Tenant UUID")
    phone_number: str = Field(..., description="Phone in E.164 format")
    name: str = Field(..., description="Contact name")
    email: str | None = Field(default=None, description="Email address")
    is_active: bool = Field(..., description="Whether contact is active")
    opted_out: bool = Field(..., description="Messaging opt-out status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}
