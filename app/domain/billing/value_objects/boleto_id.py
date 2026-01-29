"""BoletoId value object."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class BoletoId:
    """Strongly-typed identifier for Boleto aggregate."""

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("BoletoId must be a valid UUID")

    @classmethod
    def generate(cls) -> "BoletoId":
        """Generate a new random BoletoId."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "BoletoId":
        """Create BoletoId from string representation."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)
