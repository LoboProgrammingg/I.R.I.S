"""Repository ports for Collections bounded context."""

from abc import ABC, abstractmethod

from app.domain.billing.value_objects.boleto_id import BoletoId
from app.domain.collections.entities.interest_policy import InterestPolicy
from app.domain.collections.entities.reminder_schedule import ReminderSchedule
from app.domain.collections.value_objects.interest_policy_id import InterestPolicyId
from app.domain.collections.value_objects.reminder_schedule_id import ReminderScheduleId
from app.domain.identity.value_objects.tenant_id import TenantId


class InterestPolicyRepositoryPort(ABC):
    """Port for InterestPolicy persistence operations."""

    @abstractmethod
    async def get_by_tenant(self, tenant_id: TenantId) -> InterestPolicy | None:
        """Get active interest policy for a tenant."""
        ...

    @abstractmethod
    async def save(self, policy: InterestPolicy) -> InterestPolicy:
        """Persist an interest policy."""
        ...


class ReminderScheduleRepositoryPort(ABC):
    """Port for ReminderSchedule persistence operations."""

    @abstractmethod
    async def get_by_id(self, schedule_id: ReminderScheduleId) -> ReminderSchedule | None:
        """Retrieve a reminder schedule by ID."""
        ...

    @abstractmethod
    async def get_pending(self, limit: int = 100) -> list[ReminderSchedule]:
        """Get pending reminders ready for delivery."""
        ...

    @abstractmethod
    async def get_by_boleto(self, boleto_id: BoletoId) -> list[ReminderSchedule]:
        """Get all reminders for a boleto."""
        ...

    @abstractmethod
    async def save(self, schedule: ReminderSchedule) -> ReminderSchedule:
        """Persist a reminder schedule."""
        ...

    @abstractmethod
    async def cancel_for_boleto(self, boleto_id: BoletoId) -> int:
        """Cancel all pending reminders for a boleto. Returns count cancelled."""
        ...
