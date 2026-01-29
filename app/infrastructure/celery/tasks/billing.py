"""Celery tasks for Billing bounded context.

Implements payment reconciliation with Paytime.
"""

import asyncio
from datetime import datetime, timezone

from celery import shared_task

from app.application.ports.providers.paytime import PaytimeGetBoletoRequest
from app.config.logging import get_logger


logger = get_logger("billing_tasks")


@shared_task(
    name="billing.reconcile_payments",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def reconcile_payments(self, batch_size: int = 50) -> dict:
    """Reconcile boleto payments with Paytime.

    Fetches SENT boletos and checks their status in Paytime.
    Updates local state if payment was made outside webhooks.

    Idempotency: Safe to run multiple times - only updates unpaid boletos.
    """
    return asyncio.get_event_loop().run_until_complete(
        _reconcile_payments_async(batch_size)
    )


async def _reconcile_payments_async(batch_size: int) -> dict:
    """Async implementation of reconcile_payments."""
    from sqlalchemy import select

    from app.infrastructure.db.session import async_session_factory
    from app.infrastructure.db.models.billing import BoletoModel
    from app.infrastructure.db.repositories.billing import (
        BoletoRepository,
        PaymentRepository,
    )
    from app.infrastructure.db.repositories.collections import ReminderScheduleRepository
    from app.infrastructure.providers.paytime_stub import StubPaytimeProvider
    from app.domain.billing.entities.payment import Payment
    from app.domain.billing.value_objects.money import Money
    from app.domain.billing.value_objects.boleto_id import BoletoId

    reconciled = 0
    errors = 0
    now = datetime.now(timezone.utc)

    async with async_session_factory() as session:
        boleto_repo = BoletoRepository(session)
        payment_repo = PaymentRepository(session)
        reminder_repo = ReminderScheduleRepository(session)
        paytime = StubPaytimeProvider()

        result = await session.execute(
            select(BoletoModel)
            .where(
                BoletoModel.status.in_(["sent", "overdue"]),
                BoletoModel.provider_reference.isnot(None),
            )
            .limit(batch_size)
        )
        boletos = result.scalars().all()

        for boleto_model in boletos:
            try:
                request = PaytimeGetBoletoRequest(
                    provider_boleto_id=boleto_model.provider_reference
                )
                response = await paytime.get_boleto(request)

                if not response.success:
                    logger.warning(
                        "reconcile_boleto_fetch_failed",
                        boleto_id=str(boleto_model.id),
                        error=response.error_message,
                    )
                    errors += 1
                    continue

                if response.status == "paid" and boleto_model.status != "paid":
                    boleto = await boleto_repo.get_by_id(
                        BoletoId(value=boleto_model.id)
                    )
                    if boleto is None:
                        continue

                    amount_paid = Money(
                        amount_cents=response.amount_paid_cents or boleto_model.amount_cents
                    )
                    paid_at = response.paid_at or now

                    payment = Payment.create(
                        boleto_id=boleto.id,
                        amount=amount_paid,
                        paid_at=paid_at,
                        provider_reference=boleto_model.provider_reference,
                    )

                    boleto.mark_as_paid(payment.id)

                    await reminder_repo.cancel_for_boleto(boleto.id)
                    await boleto_repo.save(boleto)
                    await payment_repo.save(payment)

                    reconciled += 1

                    logger.info(
                        "reconcile_payment_found",
                        boleto_id=str(boleto_model.id),
                        amount_paid=amount_paid.amount_cents,
                    )

            except Exception as e:
                logger.error(
                    "reconcile_boleto_error",
                    boleto_id=str(boleto_model.id),
                    error=str(e),
                )
                errors += 1

        await session.commit()

    summary = {
        "processed": len(boletos) if boletos else 0,
        "reconciled": reconciled,
        "errors": errors,
        "timestamp": now.isoformat(),
    }

    logger.info("reconcile_payments_complete", **summary)
    return summary
