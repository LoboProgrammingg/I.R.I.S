"""ReminderScheduleId value object."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ReminderScheduleId:
    """Strongly-typed identifier for ReminderSchedule."""

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("ReminderScheduleId must be a valid UUID")

    @classmethod
    def generate(cls) -> "ReminderScheduleId":
        """Generate a new random ReminderScheduleId."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "ReminderScheduleId":
        """Create ReminderScheduleId from string representation."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)
