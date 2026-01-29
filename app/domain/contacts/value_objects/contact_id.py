"""ContactId value object."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ContactId:
    """Strongly-typed identifier for Contact aggregate.

    Immutable value object wrapping a UUID.
    """

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("ContactId must be a valid UUID")

    @classmethod
    def generate(cls) -> "ContactId":
        """Generate a new random ContactId."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "ContactId":
        """Create ContactId from string representation."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)
