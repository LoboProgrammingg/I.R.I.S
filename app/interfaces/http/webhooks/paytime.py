"""Paytime webhook handler.

Receives and processes webhooks from Paytime for payment events.
Verifies signature before processing.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.application.billing.dto import ProcessPaymentWebhookInput
from app.application.billing.use_cases.process_payment_webhook import (
    ProcessPaymentWebhookUseCase,
)
from app.application.ports.providers.paytime import PaytimeProviderPort
from app.config.logging import get_logger
from app.domain.billing.exceptions import BoletoNotFoundError
from app.infrastructure.db.repositories.billing import (
    BoletoRepository,
    PaymentRepository,
)
from app.infrastructure.db.repositories.collections import ReminderScheduleRepository
from app.infrastructure.db.session import get_async_session
from app.infrastructure.providers.paytime_stub import StubPaytimeProvider

router = APIRouter(prefix="/webhooks/paytime", tags=["webhooks"])
logger = get_logger("paytime_webhook")


def get_paytime_provider() -> PaytimeProviderPort:
    """Get Paytime provider for webhook verification."""
    return StubPaytimeProvider()


@router.post(
    "/payment",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid webhook payload"},
        401: {"description": "Invalid signature"},
        404: {"description": "Boleto not found"},
    },
)
async def handle_payment_webhook(
    request: Request,
    x_paytime_signature: str = Header(..., alias="X-Paytime-Signature"),
    x_paytime_timestamp: str | None = Header(None, alias="X-Paytime-Timestamp"),
    session=Depends(get_async_session),
    paytime_provider: PaytimeProviderPort = Depends(get_paytime_provider),
) -> dict:
    """Handle Paytime payment webhook.

    Verifies signature and processes payment confirmation.
    Idempotent: duplicate webhooks are safely ignored.
    """
    body = await request.body()

    if not paytime_provider.verify_webhook_signature(
        payload=body,
        signature=x_paytime_signature,
        timestamp=x_paytime_timestamp,
    ):
        logger.warning("webhook_signature_invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    try:
        payload = await request.json()
        webhook_data = paytime_provider.parse_webhook_payload(payload)
    except ValueError as e:
        logger.warning("webhook_payload_invalid", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload",
        )

    if webhook_data.event_type != "boleto.paid":
        logger.info(
            "webhook_event_ignored",
            event_type=webhook_data.event_type,
        )
        return {"status": "ignored", "event": webhook_data.event_type}

    boleto_repo = BoletoRepository(session)
    payment_repo = PaymentRepository(session)
    reminder_repo = ReminderScheduleRepository(session)

    use_case = ProcessPaymentWebhookUseCase(
        boleto_repository=boleto_repo,
        payment_repository=payment_repo,
        reminder_repository=reminder_repo,
    )

    idempotency_key = f"webhook_{webhook_data.provider_boleto_id}"

    try:
        input_dto = ProcessPaymentWebhookInput(
            provider_boleto_id=webhook_data.provider_boleto_id,
            amount_paid_cents=webhook_data.amount_paid_cents or 0,
            paid_at=webhook_data.paid_at.isoformat() if webhook_data.paid_at else "",
            idempotency_key=idempotency_key,
        )

        payment = await use_case.execute(input_dto)
        await session.commit()

        logger.info(
            "webhook_payment_processed",
            payment_id=str(payment.id.value),
            boleto_id=str(payment.boleto_id.value),
        )

        return {
            "status": "processed",
            "payment_id": str(payment.id.value),
        }

    except BoletoNotFoundError:
        logger.warning(
            "webhook_boleto_not_found",
            provider_boleto_id=webhook_data.provider_boleto_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boleto not found",
        )

    except Exception as e:
        logger.error(
            "webhook_processing_error",
            error=str(e),
            provider_boleto_id=webhook_data.provider_boleto_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed",
        )
