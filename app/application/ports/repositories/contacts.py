"""Repository ports for Contacts bounded context.

These are interfaces (protocols) that define the contract for persistence.
Infrastructure layer provides concrete implementations.
"""

from abc import ABC, abstractmethod

from app.domain.contacts.entities.contact import Contact
from app.domain.contacts.value_objects.contact_id import ContactId
from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId


class ContactRepositoryPort(ABC):
    """Port for Contact persistence operations.

    Implementations must be provided by infrastructure layer.
    All operations are tenant-scoped where applicable.
    """

    @abstractmethod
    async def get_by_id(self, contact_id: ContactId) -> Contact | None:
        """Retrieve a contact by its ID.

        Args:
            contact_id: The contact identifier

        Returns:
            Contact if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_phone(
        self, tenant_id: TenantId, phone_number: PhoneNumber
    ) -> Contact | None:
        """Retrieve a contact by phone number within a tenant.

        Args:
            tenant_id: The tenant scope
            phone_number: The phone number to search

        Returns:
            Contact if found, None otherwise
        """
        ...

    @abstractmethod
    async def save(self, contact: Contact) -> Contact:
        """Persist a contact (create or update).

        Args:
            contact: The contact to save

        Returns:
            The saved contact with any updates
        """
        ...

    @abstractmethod
    async def list_by_tenant(self, tenant_id: TenantId) -> list[Contact]:
        """List all contacts in a tenant.

        Args:
            tenant_id: The tenant scope

        Returns:
            List of contacts in the tenant
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
