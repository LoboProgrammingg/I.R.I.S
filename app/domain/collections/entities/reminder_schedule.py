"""ReminderSchedule entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.billing.value_objects.boleto_id import BoletoId
from app.domain.collections.value_objects.reminder_schedule_id import ReminderScheduleId
from app.domain.collections.value_objects.reminder_status import ReminderStatus
from app.domain.identity.value_objects.tenant_id import TenantId


@dataclass
class ReminderSchedule:
    """ReminderSchedule entity.

    Schedule for sending reminders about unpaid boletos.

    Invariants:
    - Belongs to exactly one boleto
    - Stops when boleto is PAID or CANCELLED
    """

    id: ReminderScheduleId
    tenant_id: TenantId
    boleto_id: BoletoId
    scheduled_at: datetime
    status: ReminderStatus = ReminderStatus.PENDING
    attempt_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        boleto_id: BoletoId,
        scheduled_at: datetime,
        schedule_id: ReminderScheduleId | None = None,
    ) -> "ReminderSchedule":
        """Factory method to create a new ReminderSchedule."""
        return cls(
            id=schedule_id or ReminderScheduleId.generate(),
            tenant_id=tenant_id,
            boleto_id=boleto_id,
            scheduled_at=scheduled_at,
        )

    def mark_as_sent(self) -> None:
        """Mark reminder as sent."""
        self.status = ReminderStatus.SENT
        self.attempt_count += 1

    def cancel(self) -> None:
        """Cancel this reminder schedule."""
        self.status = ReminderStatus.CANCELLED

    def increment_attempt(self) -> None:
        """Increment attempt counter."""
        self.attempt_count += 1

    def is_pending(self) -> bool:
        """Check if reminder is pending."""
        return self.status == ReminderStatus.PENDING

    def is_due(self) -> bool:
        """Check if reminder is due for delivery."""
        return self.is_pending() and self.scheduled_at <= datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReminderSchedule):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
