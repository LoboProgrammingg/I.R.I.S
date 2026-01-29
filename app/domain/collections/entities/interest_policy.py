"""InterestPolicy entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.collections.value_objects.interest_policy_id import InterestPolicyId
from app.domain.identity.value_objects.tenant_id import TenantId


@dataclass
class InterestPolicy:
    """InterestPolicy entity.

    Configuration for interest and penalty calculation per tenant.

    Invariants:
    - One active policy per tenant (MVP)
    - Daily interest rate must be non-negative
    - Grace period must be non-negative
    """

    id: InterestPolicyId
    tenant_id: TenantId
    grace_period_days: int
    daily_interest_rate_bps: int
    fixed_penalty_cents: int
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate policy invariants."""
        if self.grace_period_days < 0:
            raise ValueError("Grace period cannot be negative")
        if self.daily_interest_rate_bps < 0:
            raise ValueError("Daily interest rate cannot be negative")
        if self.fixed_penalty_cents < 0:
            raise ValueError("Fixed penalty cannot be negative")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        grace_period_days: int = 0,
        daily_interest_rate_bps: int = 0,
        fixed_penalty_cents: int = 0,
        policy_id: InterestPolicyId | None = None,
    ) -> "InterestPolicy":
        """Factory method to create a new InterestPolicy."""
        return cls(
            id=policy_id or InterestPolicyId.generate(),
            tenant_id=tenant_id,
            grace_period_days=grace_period_days,
            daily_interest_rate_bps=daily_interest_rate_bps,
            fixed_penalty_cents=fixed_penalty_cents,
        )

    def calculate_interest(self, principal_cents: int, days_overdue: int) -> int:
        """Calculate interest amount for given principal and days overdue.

        Args:
            principal_cents: Original boleto amount in cents
            days_overdue: Number of days past due date

        Returns:
            Interest amount in cents
        """
        if days_overdue <= self.grace_period_days:
            return 0

        effective_days = days_overdue - self.grace_period_days

        daily_rate = self.daily_interest_rate_bps / 10000
        interest = int(principal_cents * daily_rate * effective_days)

        return interest + self.fixed_penalty_cents

    def deactivate(self) -> None:
        """Deactivate this policy."""
        self.is_active = False
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InterestPolicy):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
