"""ReminderStatus value object."""

from enum import Enum


class ReminderStatus(str, Enum):
    """Status of a reminder schedule.

    Valid transitions:
    - PENDING → SENT, CANCELLED
    - SENT → (terminal)
    - CANCELLED → (terminal)
    """

    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        """Check if status is terminal."""
        return self in {ReminderStatus.SENT, ReminderStatus.CANCELLED}

    def can_transition_to(self, new_status: "ReminderStatus") -> bool:
        """Check if transition is valid."""
        if self.is_terminal():
            return False
        return new_status in {ReminderStatus.SENT, ReminderStatus.CANCELLED}
