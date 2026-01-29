"""BoletoStatus value object."""

from enum import Enum


class BoletoStatus(str, Enum):
    """Boleto lifecycle status.

    Valid transitions:
    - CREATED → SENT, CANCELLED
    - SENT → PAID, OVERDUE, CANCELLED
    - OVERDUE → PAID, CANCELLED
    - PAID → (terminal, no transitions)
    - CANCELLED → (terminal, no transitions)
    """

    CREATED = "created"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

    def can_transition_to(self, new_status: "BoletoStatus") -> bool:
        """Check if transition to new status is valid."""
        valid_transitions: dict[BoletoStatus, set[BoletoStatus]] = {
            BoletoStatus.CREATED: {BoletoStatus.SENT, BoletoStatus.CANCELLED},
            BoletoStatus.SENT: {
                BoletoStatus.PAID,
                BoletoStatus.OVERDUE,
                BoletoStatus.CANCELLED,
            },
            BoletoStatus.OVERDUE: {BoletoStatus.PAID, BoletoStatus.CANCELLED},
            BoletoStatus.PAID: set(),
            BoletoStatus.CANCELLED: set(),
        }
        return new_status in valid_transitions.get(self, set())

    def is_terminal(self) -> bool:
        """Check if status is terminal (no further transitions)."""
        return self in {BoletoStatus.PAID, BoletoStatus.CANCELLED}

    def is_cancellable(self) -> bool:
        """Check if boleto can be cancelled from this status."""
        return self.can_transition_to(BoletoStatus.CANCELLED)
