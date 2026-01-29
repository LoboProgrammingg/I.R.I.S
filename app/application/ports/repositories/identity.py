"""Repository ports for Identity & Tenancy bounded context.

These are interfaces (protocols) that define the contract for persistence.
Infrastructure layer provides concrete implementations.
"""

from abc import ABC, abstractmethod

from app.domain.identity.entities.tenant import Tenant
from app.domain.identity.entities.user import User
from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.identity.value_objects.user_id import UserId


class TenantRepositoryPort(ABC):
    """Port for Tenant persistence operations.

    Implementations must be provided by infrastructure layer.
    """

    @abstractmethod
    async def get_by_id(self, tenant_id: TenantId) -> Tenant | None:
        """Retrieve a tenant by its ID.

        Args:
            tenant_id: The tenant identifier

        Returns:
            Tenant if found, None otherwise
        """
        ...

    @abstractmethod
    async def save(self, tenant: Tenant) -> Tenant:
        """Persist a tenant (create or update).

        Args:
            tenant: The tenant to save

        Returns:
            The saved tenant with any updates
        """
        ...

    @abstractmethod
    async def exists(self, tenant_id: TenantId) -> bool:
        """Check if a tenant exists.

        Args:
            tenant_id: The tenant identifier

        Returns:
            True if tenant exists, False otherwise
        """
        ...


class UserRepositoryPort(ABC):
    """Port for User persistence operations.

    Implementations must be provided by infrastructure layer.
    All operations are tenant-scoped where applicable.
    """

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> User | None:
        """Retrieve a user by its ID.

        Args:
            user_id: The user identifier

        Returns:
            User if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_phone(
        self, tenant_id: TenantId, phone_number: PhoneNumber
    ) -> User | None:
        """Retrieve a user by phone number within a tenant.

        Args:
            tenant_id: The tenant scope
            phone_number: The phone number to search

        Returns:
            User if found, None otherwise
        """
        ...

    @abstractmethod
    async def save(self, user: User) -> User:
        """Persist a user (create or update).

        Args:
            user: The user to save

        Returns:
            The saved user with any updates
        """
        ...

    @abstractmethod
    async def list_by_tenant(self, tenant_id: TenantId) -> list[User]:
        """List all users in a tenant.

        Args:
            tenant_id: The tenant scope

        Returns:
            List of users in the tenant
        """
        ...

    @abstractmethod
    async def phone_exists_in_tenant(
        self, tenant_id: TenantId, phone_number: PhoneNumber
    ) -> bool:
        """Check if a phone number is already registered in a tenant.

        Args:
            tenant_id: The tenant scope
            phone_number: The phone number to check

        Returns:
            True if phone exists in tenant, False otherwise
        """
        ...
