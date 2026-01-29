"""Tenant aggregate root."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.identity.value_objects.tenant_id import TenantId


@dataclass
class Tenant:
    """Tenant aggregate root.

    Represents a logical customer/account that owns all data in the system.
    All other entities are scoped by tenant_id.

    Invariants:
    - Tenant name must not be empty
    - Tenant ID is immutable after creation
    - Inactive tenants cannot have active users
    """

    id: TenantId
    name: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate tenant invariants."""
        if not self.name or not self.name.strip():
            raise ValueError("Tenant name must not be empty")

    @classmethod
    def create(cls, name: str, tenant_id: TenantId | None = None) -> "Tenant":
        """Factory method to create a new Tenant.

        Args:
            name: Tenant display name
            tenant_id: Optional pre-generated ID, generates new if None

        Returns:
            New Tenant instance
        """
        return cls(
            id=tenant_id or TenantId.generate(),
            name=name.strip(),
            is_active=True,
        )

    def deactivate(self) -> None:
        """Deactivate the tenant.

        Inactive tenants cannot perform operations.
        """
        self.is_active = False
        self._touch()

    def activate(self) -> None:
        """Reactivate the tenant."""
        self.is_active = True
        self._touch()

    def rename(self, new_name: str) -> None:
        """Change tenant name."""
        if not new_name or not new_name.strip():
            raise ValueError("Tenant name must not be empty")
        self.name = new_name.strip()
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tenant):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
