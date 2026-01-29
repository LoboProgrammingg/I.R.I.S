"""Stub implementation of PaytimeProviderPort for testing.

Returns predictable responses without network calls.
"""

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.application.ports.providers.paytime import (
    PaytimeCancelBoletoRequest,
    PaytimeCancelBoletoResponse,
    PaytimeCreateBoletoRequest,
    PaytimeCreateBoletoResponse,
    PaytimeErrorCode,
    PaytimeGetBoletoRequest,
    PaytimeGetBoletoResponse,
    PaytimeProviderPort,
    PaytimeWebhookPayload,
)
from app.config.logging import get_logger


logger = get_logger("paytime_stub")


class StubPaytimeProvider(PaytimeProviderPort):
    """Stub Paytime provider for testing and development."""

    WEBHOOK_SECRET = "stub_webhook_secret_key"

    def __init__(self) -> None:
        self._boletos: dict[str, dict] = {}

    async def create_boleto(
        self, request: PaytimeCreateBoletoRequest
    ) -> PaytimeCreateBoletoResponse:
        """Create a boleto (stub)."""
        logger.info(
            "stub_create_boleto",
            amount_cents=request.amount_cents,
            due_date=request.due_date,
        )

        if request.amount_cents <= 0:
            return PaytimeCreateBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.INVALID_AMOUNT,
                error_message="Amount must be positive",
            )

        provider_boleto_id = f"paytime_{uuid4().hex[:16]}"
        barcode = f"23793.38128 {uuid4().hex[:8]} 12345.678901 2 {request.amount_cents:014d}"

        self._boletos[provider_boleto_id] = {
            "id": provider_boleto_id,
            "status": "pending",
            "amount_cents": request.amount_cents,
            "due_date": request.due_date,
            "created_at": datetime.now(timezone.utc),
        }

        return PaytimeCreateBoletoResponse(
            success=True,
            provider_boleto_id=provider_boleto_id,
            barcode=barcode,
            digitable_line=barcode.replace(" ", ""),
            pdf_url=f"https://stub.paytime.com/boleto/{provider_boleto_id}.pdf",
        )

    async def cancel_boleto(
        self, request: PaytimeCancelBoletoRequest
    ) -> PaytimeCancelBoletoResponse:
        """Cancel a boleto (stub)."""
        logger.info(
            "stub_cancel_boleto",
            provider_boleto_id=request.provider_boleto_id,
        )

        boleto = self._boletos.get(request.provider_boleto_id)

        if boleto is None:
            return PaytimeCancelBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.BOLETO_NOT_FOUND,
                error_message="Boleto not found",
            )

        if boleto["status"] == "paid":
            return PaytimeCancelBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.BOLETO_ALREADY_PAID,
                error_message="Cannot cancel paid boleto",
            )

        if boleto["status"] == "cancelled":
            return PaytimeCancelBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.BOLETO_ALREADY_CANCELLED,
                error_message="Boleto already cancelled",
            )

        boleto["status"] = "cancelled"
        cancelled_at = datetime.now(timezone.utc)

        return PaytimeCancelBoletoResponse(
            success=True,
            cancelled_at=cancelled_at,
        )

    async def get_boleto(
        self, request: PaytimeGetBoletoRequest
    ) -> PaytimeGetBoletoResponse:
        """Get boleto status (stub)."""
        logger.info(
            "stub_get_boleto",
            provider_boleto_id=request.provider_boleto_id,
        )

        boleto = self._boletos.get(request.provider_boleto_id)

        if boleto is None:
            return PaytimeGetBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.BOLETO_NOT_FOUND,
                error_message="Boleto not found",
            )

        return PaytimeGetBoletoResponse(
            success=True,
            provider_boleto_id=request.provider_boleto_id,
            status=boleto["status"],
            amount_cents=boleto["amount_cents"],
            amount_paid_cents=boleto.get("amount_paid_cents"),
            paid_at=boleto.get("paid_at"),
        )

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str | None = None,
    ) -> bool:
        """Verify webhook signature (stub)."""
        expected = hmac.new(
            self.WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def parse_webhook_payload(
        self, payload: dict[str, Any]
    ) -> PaytimeWebhookPayload:
        """Parse webhook payload (stub)."""
        event_type = payload.get("event")
        boleto_id = payload.get("boleto_id")

        if not event_type or not boleto_id:
            raise ValueError("Invalid webhook payload: missing event or boleto_id")

        paid_at = None
        if payload.get("paid_at"):
            paid_at = datetime.fromisoformat(payload["paid_at"].replace("Z", "+00:00"))

        return PaytimeWebhookPayload(
            event_type=event_type,
            provider_boleto_id=boleto_id,
            amount_cents=payload.get("amount_cents"),
            amount_paid_cents=payload.get("amount_paid_cents"),
            paid_at=paid_at,
            raw_payload=payload,
        )

    def simulate_payment(self, provider_boleto_id: str, amount_paid_cents: int) -> bool:
        """Simulate a payment for testing."""
        boleto = self._boletos.get(provider_boleto_id)
        if boleto is None:
            return False

        boleto["status"] = "paid"
        boleto["amount_paid_cents"] = amount_paid_cents
        boleto["paid_at"] = datetime.now(timezone.utc)
        return True
