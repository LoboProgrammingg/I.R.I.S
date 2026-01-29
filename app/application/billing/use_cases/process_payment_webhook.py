"""ProcessPaymentWebhook use case.

Processes a payment confirmation from Paytime webhook.

Invariants enforced:
- Webhook must be verified (signature)
- Boleto must exist
- Boleto must not already be paid
- Idempotency key prevents duplicate processing
- Cancels pending reminders after payment
"""

from datetime import datetime

from app.application.billing.dto import ProcessPaymentWebhookInput
from app.application.ports.repositories.billing import (
    BoletoRepositoryPort,
    PaymentRepositoryPort,
)
from app.application.ports.repositories.collections import ReminderScheduleRepositoryPort
from app.domain.billing.entities.payment import Payment
from app.domain.billing.exceptions import BoletoNotFoundError
from app.domain.billing.value_objects.money import Money


class ProcessPaymentWebhookUseCase:
    """Use case for processing payment webhook from Paytime.

    Idempotent: Uses idempotency_key to prevent duplicate processing.
    Updates Billing state (boleto → PAID) and Collections state (cancel reminders).
    """

    def __init__(
        self,
        boleto_repository: BoletoRepositoryPort,
        payment_repository: PaymentRepositoryPort,
        reminder_repository: ReminderScheduleRepositoryPort,
    ) -> None:
        self._boleto_repository = boleto_repository
        self._payment_repository = payment_repository
        self._reminder_repository = reminder_repository

    async def execute(self, input_dto: ProcessPaymentWebhookInput) -> Payment:
        """Execute the ProcessPaymentWebhook use case.

        Args:
            input_dto: Payment webhook data

        Returns:
            Created Payment domain entity

        Raises:
            BoletoNotFoundError: If boleto does not exist
            BoletoAlreadyPaidError: If boleto is already paid
        """
        existing_payment = await self._payment_repository.get_by_idempotency_key(
            input_dto.idempotency_key
        )
        if existing_payment is not None:
            return existing_payment

        boleto = await self._boleto_repository.get_by_provider_reference(
            input_dto.provider_boleto_id
        )
        if boleto is None:
            raise BoletoNotFoundError(input_dto.provider_boleto_id)

        if boleto.is_paid():
            existing = await self._payment_repository.get_by_boleto_id(boleto.id)
            if existing:
                return existing

        amount_paid = Money(amount_cents=input_dto.amount_paid_cents)
        paid_at = datetime.fromisoformat(input_dto.paid_at.replace("Z", "+00:00"))

        payment = Payment.create(
            boleto_id=boleto.id,
            amount=amount_paid,
            paid_at=paid_at,
            provider_reference=input_dto.provider_boleto_id,
        )

        boleto.mark_as_paid(payment.id)

        await self._reminder_repository.cancel_for_boleto(boleto.id)

        await self._boleto_repository.save(boleto)
        saved_payment = await self._payment_repository.save(payment)

        return saved_payment
