"""Pydantic schemas for Identity & Tenancy HTTP endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateTenantRequest(BaseModel):
    """Request schema for creating a tenant."""

    name: str = Field(..., min_length=1, max_length=255, description="Tenant name")


class TenantResponse(BaseModel):
    """Response schema for tenant data."""

    id: str = Field(..., description="Tenant UUID")
    name: str = Field(..., description="Tenant name")
    is_active: bool = Field(..., description="Whether tenant is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class CreateUserRequest(BaseModel):
    """Request schema for creating a user."""

    phone_number: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Phone number in E.164 format",
        examples=["+5511999998888"],
    )
    name: str = Field(..., min_length=1, max_length=255, description="User name")
    role: str = Field(
        default="user",
        pattern="^(admin|user)$",
        description="User role: admin or user",
    )


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: str = Field(..., description="User UUID")
    tenant_id: str = Field(..., description="Tenant UUID")
    phone_number: str = Field(..., description="Phone in E.164 format")
    name: str = Field(..., description="User name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
