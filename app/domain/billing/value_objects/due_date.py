"""DueDate value object."""

from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass(frozen=True, slots=True)
class DueDate:
    """Value object representing a boleto due date."""

    value: date

    def __post_init__(self) -> None:
        if not isinstance(self.value, date):
            raise ValueError("DueDate must be a valid date")

    @classmethod
    def from_string(cls, value: str) -> "DueDate":
        """Create DueDate from ISO format string (YYYY-MM-DD)."""
        return cls(value=date.fromisoformat(value))

    @classmethod
    def from_datetime(cls, dt: datetime) -> "DueDate":
        """Create DueDate from datetime."""
        return cls(value=dt.date())

    def is_past(self) -> bool:
        """Check if due date has passed."""
        return self.value < datetime.now(timezone.utc).date()

    def is_today(self) -> bool:
        """Check if due date is today."""
        return self.value == datetime.now(timezone.utc).date()

    def is_future(self) -> bool:
        """Check if due date is in the future."""
        return self.value > datetime.now(timezone.utc).date()

    def __str__(self) -> str:
        return self.value.isoformat()

    def __hash__(self) -> int:
        return hash(self.value)
