"""DTOs for Collections use cases."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateInterestPolicyInput:
    """Input for CreateInterestPolicy use case."""

    tenant_id: str
    grace_period_days: int = 0
    daily_interest_rate_bps: int = 0
    fixed_penalty_cents: int = 0


@dataclass(frozen=True)
class MarkOverdueInput:
    """Input for MarkOverdue use case (batch)."""

    batch_size: int = 100


@dataclass(frozen=True)
class ApplyInterestInput:
    """Input for ApplyInterest use case (batch)."""

    batch_size: int = 100


@dataclass(frozen=True)
class ScheduleReminderInput:
    """Input for ScheduleReminder use case."""

    tenant_id: str
    boleto_id: str
    scheduled_at: datetime
