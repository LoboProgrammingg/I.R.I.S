"""Collections domain exceptions."""


class CollectionsDomainError(Exception):
    """Base exception for Collections domain errors."""

    pass


class InterestPolicyNotFoundError(CollectionsDomainError):
    """Raised when an interest policy is not found."""

    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        super().__init__(f"Interest policy not found for tenant: {tenant_id}")


class ReminderScheduleNotFoundError(CollectionsDomainError):
    """Raised when a reminder schedule is not found."""

    def __init__(self, schedule_id: str) -> None:
        self.schedule_id = schedule_id
        super().__init__(f"Reminder schedule not found: {schedule_id}")


class InvalidInterestRateError(CollectionsDomainError):
    """Raised when an invalid interest rate is specified."""

    def __init__(self, rate_bps: int) -> None:
        self.rate_bps = rate_bps
        super().__init__(f"Invalid interest rate: {rate_bps} basis points")
