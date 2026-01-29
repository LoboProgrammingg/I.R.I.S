"""Collections domain events.

These are definitions only - event publishing infrastructure comes later.
"""

from dataclasses import dataclass
from datetime import datetime

from app.domain.billing.value_objects.boleto_id import BoletoId
from app.domain.collections.value_objects.interest_policy_id import InterestPolicyId
from app.domain.collections.value_objects.reminder_schedule_id import ReminderScheduleId


@dataclass(frozen=True)
class InterestPolicyCreated:
    """Event raised when a new interest policy is created."""

    policy_id: InterestPolicyId
    tenant_id: str
    daily_interest_rate_bps: int
    occurred_at: datetime


@dataclass(frozen=True)
class InterestApplied:
    """Event raised when interest is applied to a boleto."""

    boleto_id: BoletoId
    original_amount_cents: int
    interest_amount_cents: int
    new_total_cents: int
    occurred_at: datetime


@dataclass(frozen=True)
class ReminderScheduled:
    """Event raised when a reminder is scheduled."""

    schedule_id: ReminderScheduleId
    boleto_id: BoletoId
    scheduled_at: datetime
    occurred_at: datetime


@dataclass(frozen=True)
class ReminderSent:
    """Event raised when a reminder is sent."""

    schedule_id: ReminderScheduleId
    boleto_id: BoletoId
    occurred_at: datetime
