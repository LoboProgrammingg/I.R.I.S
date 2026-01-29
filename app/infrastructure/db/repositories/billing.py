"""Repository implementations for Billing bounded context."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories.billing import (
    BoletoRepositoryPort,
    PaymentRepositoryPort,
)
from app.domain.billing.entities.boleto import Boleto
from app.domain.billing.entities.payment import Payment
from app.domain.billing.value_objects.boleto_id import BoletoId
from app.domain.billing.value_objects.boleto_status import BoletoStatus
from app.domain.billing.value_objects.due_date import DueDate
from app.domain.billing.value_objects.money import Money
from app.domain.billing.value_objects.payment_id import PaymentId
from app.domain.contacts.value_objects.contact_id import ContactId
from app.domain.identity.value_objects.tenant_id import TenantId
from app.infrastructure.db.models.billing import BoletoModel, PaymentModel


class BoletoRepository(BoletoRepositoryPort):
    """SQLAlchemy implementation of BoletoRepositoryPort."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, boleto_id: BoletoId) -> Boleto | None:
        """Retrieve a boleto by its ID."""
        result = await self._session.execute(
            select(BoletoModel).where(BoletoModel.id == boleto_id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def save(self, boleto: Boleto) -> Boleto:
        """Persist a boleto (create or update)."""
        existing = await self._session.get(BoletoModel, boleto.id.value)

        if existing is None:
            model = self._to_model(boleto)
            self._session.add(model)
        else:
            existing.status = boleto.status.value
            existing.provider_reference = boleto.provider_reference
            existing.updated_at = boleto.updated_at
            model = existing

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_provider_reference(self, provider_reference: str) -> Boleto | None:
        """Retrieve a boleto by its Paytime provider reference."""
        result = await self._session.execute(
            select(BoletoModel).where(
                BoletoModel.provider_reference == provider_reference
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def exists_by_idempotency_key(
        self, tenant_id: TenantId, idempotency_key: str
    ) -> bool:
        """Check if a boleto with given idempotency key exists."""
        result = await self._session.execute(
            select(BoletoModel.id).where(
                BoletoModel.tenant_id == tenant_id.value,
                BoletoModel.idempotency_key == idempotency_key,
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_domain(model: BoletoModel) -> Boleto:
        """Map SQLAlchemy model to domain entity."""
        return Boleto(
            id=BoletoId(value=model.id),
            tenant_id=TenantId(value=model.tenant_id),
            contact_id=ContactId(value=model.contact_id),
            amount=Money(amount_cents=model.amount_cents, currency=model.currency),
            due_date=DueDate.from_datetime(model.due_date),
            status=BoletoStatus(model.status),
            idempotency_key=model.idempotency_key,
            provider_reference=model.provider_reference,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(boleto: Boleto) -> BoletoModel:
        """Map domain entity to SQLAlchemy model."""
        return BoletoModel(
            id=boleto.id.value,
            tenant_id=boleto.tenant_id.value,
            contact_id=boleto.contact_id.value,
            amount_cents=boleto.amount.amount_cents,
            currency=boleto.amount.currency,
            due_date=datetime.combine(
                boleto.due_date.value,
                datetime.min.time(),
                tzinfo=boleto.created_at.tzinfo,
            ),
            status=boleto.status.value,
            idempotency_key=boleto.idempotency_key,
            provider_reference=boleto.provider_reference,
            created_at=boleto.created_at,
            updated_at=boleto.updated_at,
        )


class PaymentRepository(PaymentRepositoryPort):
    """SQLAlchemy implementation of PaymentRepositoryPort."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_boleto_id(self, boleto_id: BoletoId) -> Payment | None:
        """Retrieve payment for a boleto."""
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.boleto_id == boleto_id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        """Retrieve payment by idempotency key (provider_reference)."""
        result = await self._session.execute(
            select(PaymentModel).where(
                PaymentModel.provider_reference == idempotency_key
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def save(self, payment: Payment) -> Payment:
        """Persist a payment."""
        model = self._to_model(payment)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: PaymentModel) -> Payment:
        """Map SQLAlchemy model to domain entity."""
        return Payment(
            id=PaymentId(value=model.id),
            boleto_id=BoletoId(value=model.boleto_id),
            amount=Money(amount_cents=model.amount_cents, currency=model.currency),
            paid_at=model.paid_at,
            provider_reference=model.provider_reference,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(payment: Payment) -> PaymentModel:
        """Map domain entity to SQLAlchemy model."""
        return PaymentModel(
            id=payment.id.value,
            boleto_id=payment.boleto_id.value,
            amount_cents=payment.amount.amount_cents,
            currency=payment.amount.currency,
            paid_at=payment.paid_at,
            provider_reference=payment.provider_reference,
            created_at=payment.created_at,
        )
