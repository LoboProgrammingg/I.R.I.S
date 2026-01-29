"""PaymentId value object."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class PaymentId:
    """Strongly-typed identifier for Payment entity."""

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("PaymentId must be a valid UUID")

    @classmethod
    def generate(cls) -> "PaymentId":
        """Generate a new random PaymentId."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "PaymentId":
        """Create PaymentId from string representation."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)
