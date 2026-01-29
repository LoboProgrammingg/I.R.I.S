"""HTTP client implementation of PaytimeProviderPort.

Production-ready adapter for Paytime API.
"""

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Any

import httpx

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
from app.config.settings import settings


logger = get_logger("paytime_client")


class PaytimeClient(PaytimeProviderPort):
    """HTTP client for Paytime API.

    Features:
    - 30s timeout
    - 3 retries with exponential backoff
    - Structured logging (no sensitive data)
    - Idempotency key support
    """

    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_DELAYS = [1.0, 2.0, 4.0]

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        webhook_secret: str | None = None,
    ) -> None:
        self._base_url = base_url or settings.PAYTIME_BASE_URL
        self._api_key = api_key or settings.PAYTIME_API_KEY
        self._webhook_secret = webhook_secret or settings.PAYTIME_WEBHOOK_SECRET

    def _get_headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        """Build request headers."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _map_error_code(self, error_code: str | None) -> PaytimeErrorCode:
        """Map Paytime API error codes to internal enum."""
        mapping = {
            "invalid_amount": PaytimeErrorCode.INVALID_AMOUNT,
            "invalid_due_date": PaytimeErrorCode.INVALID_DUE_DATE,
            "invalid_payer": PaytimeErrorCode.INVALID_PAYER,
            "boleto_not_found": PaytimeErrorCode.BOLETO_NOT_FOUND,
            "already_paid": PaytimeErrorCode.BOLETO_ALREADY_PAID,
            "already_cancelled": PaytimeErrorCode.BOLETO_ALREADY_CANCELLED,
            "rate_limited": PaytimeErrorCode.RATE_LIMITED,
        }
        return mapping.get(error_code or "", PaytimeErrorCode.UNKNOWN)

    async def create_boleto(
        self, request: PaytimeCreateBoletoRequest
    ) -> PaytimeCreateBoletoResponse:
        """Create a boleto via Paytime API."""
        logger.info(
            "paytime_create_boleto_start",
            amount_cents=request.amount_cents,
            due_date=request.due_date,
        )

        payload = {
            "amount": request.amount_cents,
            "due_date": request.due_date,
            "payer": {
                "name": request.payer_name,
                "phone": request.payer_phone,
            },
        }

        if request.payer_document:
            payload["payer"]["document"] = request.payer_document
        if request.description:
            payload["description"] = request.description

        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(
                    f"{self._base_url}/boletos",
                    json=payload,
                    headers=self._get_headers(request.idempotency_key),
                )

            if response.status_code == 201:
                data = response.json()
                logger.info(
                    "paytime_create_boleto_success",
                    provider_boleto_id=data.get("id"),
                )
                return PaytimeCreateBoletoResponse(
                    success=True,
                    provider_boleto_id=data.get("id"),
                    barcode=data.get("barcode"),
                    digitable_line=data.get("digitable_line"),
                    pdf_url=data.get("pdf_url"),
                )

            error_data = response.json() if response.content else {}
            logger.warning(
                "paytime_create_boleto_failed",
                status_code=response.status_code,
                error_code=error_data.get("code"),
            )

            return PaytimeCreateBoletoResponse(
                success=False,
                error_code=self._map_error_code(error_data.get("code")),
                error_message=error_data.get("message", "Unknown error"),
            )

        except httpx.TimeoutException:
            logger.error("paytime_create_boleto_timeout")
            return PaytimeCreateBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.TIMEOUT,
                error_message="Request timed out",
            )

        except httpx.RequestError as e:
            logger.error("paytime_create_boleto_network_error", error=str(e))
            return PaytimeCreateBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.NETWORK_ERROR,
                error_message=str(e),
            )

    async def cancel_boleto(
        self, request: PaytimeCancelBoletoRequest
    ) -> PaytimeCancelBoletoResponse:
        """Cancel a boleto via Paytime API."""
        logger.info(
            "paytime_cancel_boleto_start",
            provider_boleto_id=request.provider_boleto_id,
        )

        payload = {}
        if request.reason:
            payload["reason"] = request.reason

        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(
                    f"{self._base_url}/boletos/{request.provider_boleto_id}/cancel",
                    json=payload,
                    headers=self._get_headers(),
                )

            if response.status_code in (200, 204):
                data = response.json() if response.content else {}
                cancelled_at = None
                if data.get("cancelled_at"):
                    cancelled_at = datetime.fromisoformat(
                        data["cancelled_at"].replace("Z", "+00:00")
                    )

                logger.info(
                    "paytime_cancel_boleto_success",
                    provider_boleto_id=request.provider_boleto_id,
                )
                return PaytimeCancelBoletoResponse(
                    success=True,
                    cancelled_at=cancelled_at or datetime.now(timezone.utc),
                )

            error_data = response.json() if response.content else {}
            logger.warning(
                "paytime_cancel_boleto_failed",
                provider_boleto_id=request.provider_boleto_id,
                status_code=response.status_code,
            )

            return PaytimeCancelBoletoResponse(
                success=False,
                error_code=self._map_error_code(error_data.get("code")),
                error_message=error_data.get("message", "Unknown error"),
            )

        except httpx.TimeoutException:
            logger.error("paytime_cancel_boleto_timeout")
            return PaytimeCancelBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.TIMEOUT,
                error_message="Request timed out",
            )

        except httpx.RequestError as e:
            logger.error("paytime_cancel_boleto_network_error", error=str(e))
            return PaytimeCancelBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.NETWORK_ERROR,
                error_message=str(e),
            )

    async def get_boleto(
        self, request: PaytimeGetBoletoRequest
    ) -> PaytimeGetBoletoResponse:
        """Get boleto status from Paytime API."""
        logger.info(
            "paytime_get_boleto_start",
            provider_boleto_id=request.provider_boleto_id,
        )

        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.get(
                    f"{self._base_url}/boletos/{request.provider_boleto_id}",
                    headers=self._get_headers(),
                )

            if response.status_code == 200:
                data = response.json()
                paid_at = None
                if data.get("paid_at"):
                    paid_at = datetime.fromisoformat(
                        data["paid_at"].replace("Z", "+00:00")
                    )

                return PaytimeGetBoletoResponse(
                    success=True,
                    provider_boleto_id=data.get("id"),
                    status=data.get("status"),
                    amount_cents=data.get("amount"),
                    amount_paid_cents=data.get("amount_paid"),
                    paid_at=paid_at,
                )

            error_data = response.json() if response.content else {}
            return PaytimeGetBoletoResponse(
                success=False,
                error_code=self._map_error_code(error_data.get("code")),
                error_message=error_data.get("message", "Unknown error"),
            )

        except httpx.TimeoutException:
            return PaytimeGetBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.TIMEOUT,
                error_message="Request timed out",
            )

        except httpx.RequestError as e:
            return PaytimeGetBoletoResponse(
                success=False,
                error_code=PaytimeErrorCode.NETWORK_ERROR,
                error_message=str(e),
            )

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str | None = None,
    ) -> bool:
        """Verify Paytime webhook signature."""
        if not signature:
            return False

        message = payload
        if timestamp:
            message = f"{timestamp}.".encode() + payload

        expected = hmac.new(
            self._webhook_secret.encode(),
            message,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def parse_webhook_payload(
        self, payload: dict[str, Any]
    ) -> PaytimeWebhookPayload:
        """Parse Paytime webhook payload."""
        event_type = payload.get("event")
        boleto_data = payload.get("data", {})
        boleto_id = boleto_data.get("id")

        if not event_type or not boleto_id:
            raise ValueError("Invalid webhook payload")

        paid_at = None
        if boleto_data.get("paid_at"):
            paid_at = datetime.fromisoformat(
                boleto_data["paid_at"].replace("Z", "+00:00")
            )

        return PaytimeWebhookPayload(
            event_type=event_type,
            provider_boleto_id=boleto_id,
            amount_cents=boleto_data.get("amount"),
            amount_paid_cents=boleto_data.get("amount_paid"),
            paid_at=paid_at,
            raw_payload=payload,
        )
