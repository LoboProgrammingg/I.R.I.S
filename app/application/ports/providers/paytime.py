"""Paytime provider port for boleto operations.

Defines the contract for Paytime integration.
No direct API calls in this file - only interface definition.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class PaytimeErrorCode(str, Enum):
    """Error codes from Paytime API."""

    INVALID_AMOUNT = "invalid_amount"
    INVALID_DUE_DATE = "invalid_due_date"
    INVALID_PAYER = "invalid_payer"
    BOLETO_NOT_FOUND = "boleto_not_found"
    BOLETO_ALREADY_PAID = "boleto_already_paid"
    BOLETO_ALREADY_CANCELLED = "boleto_already_cancelled"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PaytimeCreateBoletoRequest:
    """Request to create a boleto in Paytime."""

    amount_cents: int
    due_date: str  # ISO format YYYY-MM-DD
    payer_name: str
    payer_phone: str
    payer_document: str | None = None
    description: str | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True)
class PaytimeCreateBoletoResponse:
    """Response from Paytime boleto creation."""

    success: bool
    provider_boleto_id: str | None = None
    barcode: str | None = None
    digitable_line: str | None = None
    pdf_url: str | None = None
    error_code: PaytimeErrorCode | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class PaytimeCancelBoletoRequest:
    """Request to cancel a boleto in Paytime."""

    provider_boleto_id: str
    reason: str | None = None


@dataclass(frozen=True)
class PaytimeCancelBoletoResponse:
    """Response from Paytime boleto cancellation."""

    success: bool
    cancelled_at: datetime | None = None
    error_code: PaytimeErrorCode | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class PaytimeGetBoletoRequest:
    """Request to get boleto status from Paytime."""

    provider_boleto_id: str


@dataclass(frozen=True)
class PaytimeGetBoletoResponse:
    """Response from Paytime boleto status query."""

    success: bool
    provider_boleto_id: str | None = None
    status: str | None = None  # pending, paid, cancelled, expired
    amount_cents: int | None = None
    amount_paid_cents: int | None = None
    paid_at: datetime | None = None
    error_code: PaytimeErrorCode | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class PaytimeWebhookPayload:
    """Parsed and verified webhook payload from Paytime."""

    event_type: str  # boleto.paid, boleto.cancelled, boleto.expired
    provider_boleto_id: str
    amount_cents: int | None = None
    amount_paid_cents: int | None = None
    paid_at: datetime | None = None
    raw_payload: dict[str, Any] | None = None


class PaytimeProviderPort(ABC):
    """Port for Paytime boleto operations.

    All implementations must:
    - Handle timeouts (30s max)
    - Retry on transient errors (up to 3 times)
    - Log operations (no sensitive data)
    - Support idempotency where applicable
    """

    @abstractmethod
    async def create_boleto(
        self, request: PaytimeCreateBoletoRequest
    ) -> PaytimeCreateBoletoResponse:
        """Create a boleto in Paytime.

        Args:
            request: Boleto creation data

        Returns:
            Response with provider_boleto_id if successful
        """
        ...

    @abstractmethod
    async def cancel_boleto(
        self, request: PaytimeCancelBoletoRequest
    ) -> PaytimeCancelBoletoResponse:
        """Cancel a boleto in Paytime.

        Args:
            request: Cancellation data

        Returns:
            Response with cancellation status
        """
        ...

    @abstractmethod
    async def get_boleto(
        self, request: PaytimeGetBoletoRequest
    ) -> PaytimeGetBoletoResponse:
        """Get boleto status from Paytime.

        Used for reconciliation.

        Args:
            request: Boleto query data

        Returns:
            Response with current boleto status
        """
        ...

    @abstractmethod
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str | None = None,
    ) -> bool:
        """Verify webhook signature.

        Args:
            payload: Raw webhook payload bytes
            signature: Signature header value
            timestamp: Optional timestamp for replay protection

        Returns:
            True if signature is valid
        """
        ...

    @abstractmethod
    def parse_webhook_payload(
        self, payload: dict[str, Any]
    ) -> PaytimeWebhookPayload:
        """Parse and validate webhook payload.

        Args:
            payload: Parsed JSON payload

        Returns:
            Structured webhook payload

        Raises:
            ValueError: If payload is invalid
        """
        ...
