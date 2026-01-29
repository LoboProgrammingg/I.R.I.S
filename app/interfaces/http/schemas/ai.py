"""Pydantic schemas for AI HTTP endpoints."""

from pydantic import BaseModel, Field


class AIMessageRequest(BaseModel):
    """Request for /ai/message endpoint."""

    conversation_id: str | None = Field(
        None,
        description="Existing conversation ID or None for new conversation",
    )
    tenant_id: str = Field(..., description="Tenant identifier")
    text: str = Field(..., min_length=1, max_length=2000, description="User message")


class AIMessageResponse(BaseModel):
    """Response from /ai/message endpoint."""

    conversation_id: str = Field(..., description="Conversation identifier")
    response: str = Field(..., description="AI response text")
    requires_confirmation: bool = Field(
        False,
        description="Whether user confirmation is required",
    )
    suggested_action: str | None = Field(
        None,
        description="Suggested action (e.g., 'create_boleto')",
    )
    intent: str | None = Field(None, description="Detected intent")


class AIConfirmRequest(BaseModel):
    """Request for /ai/confirm endpoint."""

    conversation_id: str = Field(..., description="Conversation identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    confirmed: bool = Field(..., description="User confirmation (true/false)")


class AIConfirmResponse(BaseModel):
    """Response from /ai/confirm endpoint."""

    conversation_id: str = Field(..., description="Conversation identifier")
    response: str = Field(..., description="AI response text")
    action_executed: bool = Field(
        False,
        description="Whether the action was executed",
    )
    result: dict | None = Field(None, description="Action result if executed")


class AIErrorResponse(BaseModel):
    """Error response for AI endpoints."""

    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    conversation_id: str | None = Field(None, description="Conversation ID if available")
