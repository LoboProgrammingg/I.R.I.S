"""Repository implementations for Collections bounded context."""

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories.collections import (
    InterestPolicyRepositoryPort,
    ReminderScheduleRepositoryPort,
)
from app.domain.billing.value_objects.boleto_id import BoletoId
from app.domain.collections.entities.interest_policy import InterestPolicy
from app.domain.collections.entities.reminder_schedule import ReminderSchedule
from app.domain.collections.value_objects.interest_policy_id import InterestPolicyId
from app.domain.collections.value_objects.reminder_schedule_id import ReminderScheduleId
from app.domain.collections.value_objects.reminder_status import ReminderStatus
from app.domain.identity.value_objects.tenant_id import TenantId
from app.infrastructure.db.models.collections import (
    InterestPolicyModel,
    ReminderScheduleModel,
)


class InterestPolicyRepository(InterestPolicyRepositoryPort):
    """SQLAlchemy implementation of InterestPolicyRepositoryPort."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_tenant(self, tenant_id: TenantId) -> InterestPolicy | None:
        """Get active interest policy for a tenant."""
        result = await self._session.execute(
            select(InterestPolicyModel).where(
                InterestPolicyModel.tenant_id == tenant_id.value,
                InterestPolicyModel.is_active == True,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def save(self, policy: InterestPolicy) -> InterestPolicy:
        """Persist an interest policy."""
        existing = await self._session.get(InterestPolicyModel, policy.id.value)

        if existing is None:
            model = self._to_model(policy)
            self._session.add(model)
        else:
            existing.grace_period_days = policy.grace_period_days
            existing.daily_interest_rate_bps = policy.daily_interest_rate_bps
            existing.fixed_penalty_cents = policy.fixed_penalty_cents
            existing.is_active = policy.is_active
            existing.updated_at = policy.updated_at
            model = existing

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: InterestPolicyModel) -> InterestPolicy:
        return InterestPolicy(
            id=InterestPolicyId(value=model.id),
            tenant_id=TenantId(value=model.tenant_id),
            grace_period_days=model.grace_period_days,
            daily_interest_rate_bps=model.daily_interest_rate_bps,
            fixed_penalty_cents=model.fixed_penalty_cents,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(policy: InterestPolicy) -> InterestPolicyModel:
        return InterestPolicyModel(
            id=policy.id.value,
            tenant_id=policy.tenant_id.value,
            grace_period_days=policy.grace_period_days,
            daily_interest_rate_bps=policy.daily_interest_rate_bps,
            fixed_penalty_cents=policy.fixed_penalty_cents,
            is_active=policy.is_active,
            created_at=policy.created_at,
            updated_at=policy.updated_at,
        )


class ReminderScheduleRepository(ReminderScheduleRepositoryPort):
    """SQLAlchemy implementation of ReminderScheduleRepositoryPort."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, schedule_id: ReminderScheduleId) -> ReminderSchedule | None:
        result = await self._session.execute(
            select(ReminderScheduleModel).where(
                ReminderScheduleModel.id == schedule_id.value
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_pending(self, limit: int = 100) -> list[ReminderSchedule]:
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(ReminderScheduleModel)
            .where(
                ReminderScheduleModel.status == "pending",
                ReminderScheduleModel.scheduled_at <= now,
            )
            .order_by(ReminderScheduleModel.scheduled_at)
            .limit(limit)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_boleto(self, boleto_id: BoletoId) -> list[ReminderSchedule]:
        result = await self._session.execute(
            select(ReminderScheduleModel).where(
                ReminderScheduleModel.boleto_id == boleto_id.value
            )
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def save(self, schedule: ReminderSchedule) -> ReminderSchedule:
        existing = await self._session.get(ReminderScheduleModel, schedule.id.value)

        if existing is None:
            model = self._to_model(schedule)
            self._session.add(model)
        else:
            existing.status = schedule.status.value
            existing.attempt_count = schedule.attempt_count
            model = existing

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def cancel_for_boleto(self, boleto_id: BoletoId) -> int:
        result = await self._session.execute(
            update(ReminderScheduleModel)
            .where(
                ReminderScheduleModel.boleto_id == boleto_id.value,
                ReminderScheduleModel.status == "pending",
            )
            .values(status="cancelled")
        )
        return result.rowcount

    @staticmethod
    def _to_domain(model: ReminderScheduleModel) -> ReminderSchedule:
        return ReminderSchedule(
            id=ReminderScheduleId(value=model.id),
            tenant_id=TenantId(value=model.tenant_id),
            boleto_id=BoletoId(value=model.boleto_id),
            scheduled_at=model.scheduled_at,
            status=ReminderStatus(model.status),
            attempt_count=model.attempt_count,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(schedule: ReminderSchedule) -> ReminderScheduleModel:
        return ReminderScheduleModel(
            id=schedule.id.value,
            tenant_id=schedule.tenant_id.value,
            boleto_id=schedule.boleto_id.value,
            scheduled_at=schedule.scheduled_at,
            status=schedule.status.value,
            attempt_count=schedule.attempt_count,
            created_at=schedule.created_at,
        )
