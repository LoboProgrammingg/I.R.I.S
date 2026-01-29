"""UserRole value object."""

from enum import Enum


class UserRole(Enum):
    """User role within a tenant.

    MVP scope: simple two-level hierarchy.
    Future: fine-grained permissions.
    """

    ADMIN = "admin"
    USER = "user"

    def is_admin(self) -> bool:
        """Check if role has admin privileges."""
        return self == UserRole.ADMIN
