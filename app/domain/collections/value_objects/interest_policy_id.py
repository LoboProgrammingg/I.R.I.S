"""InterestPolicyId value object."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class InterestPolicyId:
    """Strongly-typed identifier for InterestPolicy."""

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("InterestPolicyId must be a valid UUID")

    @classmethod
    def generate(cls) -> "InterestPolicyId":
        """Generate a new random InterestPolicyId."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "InterestPolicyId":
        """Create InterestPolicyId from string representation."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)
