"""DeliveryStatus value object."""

from enum import Enum


class DeliveryStatus(str, Enum):
    """Delivery status for outbox items.

    Valid transitions:
    - PENDING → SENT, FAILED, RETRYING
    - RETRYING → SENT, FAILED
    - SENT → (terminal)
    - FAILED → (terminal)
    """

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"

    def can_transition_to(self, new_status: "DeliveryStatus") -> bool:
        """Check if transition to new status is valid."""
        valid_transitions: dict[DeliveryStatus, set[DeliveryStatus]] = {
            DeliveryStatus.PENDING: {
                DeliveryStatus.SENT,
                DeliveryStatus.FAILED,
                DeliveryStatus.RETRYING,
            },
            DeliveryStatus.RETRYING: {
                DeliveryStatus.SENT,
                DeliveryStatus.FAILED,
            },
            DeliveryStatus.SENT: set(),
            DeliveryStatus.FAILED: set(),
        }
        return new_status in valid_transitions.get(self, set())

    def is_terminal(self) -> bool:
        """Check if status is terminal."""
        return self in {DeliveryStatus.SENT, DeliveryStatus.FAILED}

    def is_retriable(self) -> bool:
        """Check if item can be retried."""
        return self in {DeliveryStatus.PENDING, DeliveryStatus.RETRYING}
