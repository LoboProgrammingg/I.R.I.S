"""User entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.identity.value_objects.user_id import UserId
from app.domain.identity.value_objects.user_role import UserRole


@dataclass
class User:
    """User entity within a Tenant.

    Represents a human operator who can perform actions in the system.
    Users are scoped to exactly one tenant.

    Invariants:
    - User must belong to exactly one tenant
    - Phone number must be unique within a tenant (enforced by repository)
    - Phone number must be valid E.164 format (enforced by PhoneNumber VO)
    - User role must be explicitly set
    - User ID is immutable after creation
    - Inactive users cannot perform operations
    """

    id: UserId
    tenant_id: TenantId
    phone_number: PhoneNumber
    name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate user invariants."""
        if not self.name or not self.name.strip():
            raise ValueError("User name must not be empty")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        phone_number: PhoneNumber,
        name: str,
        role: UserRole = UserRole.USER,
        user_id: UserId | None = None,
    ) -> "User":
        """Factory method to create a new User.

        Args:
            tenant_id: Owning tenant
            phone_number: E.164 normalized phone
            name: User display name
            role: User role (defaults to USER)
            user_id: Optional pre-generated ID

        Returns:
            New User instance
        """
        return cls(
            id=user_id or UserId.generate(),
            tenant_id=tenant_id,
            phone_number=phone_number,
            name=name.strip(),
            role=role,
            is_active=True,
        )

    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False
        self._touch()

    def activate(self) -> None:
        """Reactivate the user."""
        self.is_active = True
        self._touch()

    def change_role(self, new_role: UserRole) -> None:
        """Change user role."""
        self.role = new_role
        self._touch()

    def rename(self, new_name: str) -> None:
        """Change user name."""
        if not new_name or not new_name.strip():
            raise ValueError("User name must not be empty")
        self.name = new_name.strip()
        self._touch()

    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role.is_admin()

    def can_operate(self) -> bool:
        """Check if user can perform operations."""
        return self.is_active

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
