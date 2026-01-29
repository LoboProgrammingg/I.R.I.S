"""TenantId value object."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class TenantId:
    """Strongly-typed identifier for Tenant aggregate.

    Immutable value object wrapping a UUID.
    """

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("TenantId must be a valid UUID")

    @classmethod
    def generate(cls) -> "TenantId":
        """Generate a new random TenantId."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "TenantId":
        """Create TenantId from string representation."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)
