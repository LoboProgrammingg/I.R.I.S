"""UserId value object."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class UserId:
    """Strongly-typed identifier for User entity.

    Immutable value object wrapping a UUID.
    """

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("UserId must be a valid UUID")

    @classmethod
    def generate(cls) -> "UserId":
        """Generate a new random UserId."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "UserId":
        """Create UserId from string representation."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)
