"""CreateContact use case.

Creates a new contact within a tenant.

Invariants enforced:
- Contact name must not be empty (domain entity validation)
- Phone number must be valid E.164 (PhoneNumber value object)
- Phone number must be unique within tenant (repository check)
- Tenant must exist (repository check via TenantRepositoryPort)
"""

from app.application.contacts.dto import CreateContactInput
from app.application.ports.repositories.contacts import ContactRepositoryPort
from app.application.ports.repositories.identity import TenantRepositoryPort
from app.domain.contacts.entities.contact import Contact
from app.domain.contacts.exceptions import ContactPhoneAlreadyExistsError
from app.domain.identity.exceptions import TenantNotFoundError
from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId


class CreateContactUseCase:
    """Use case for creating a new contact within a tenant.

    Responsibilities:
    - Validate tenant exists
    - Validate phone uniqueness within tenant
    - Create domain entity with validated value objects
    - Persist via repository

    Does NOT handle:
    - Authentication / authorization
    - Messaging / notifications
    """

    def __init__(
        self,
        contact_repository: ContactRepositoryPort,
        tenant_repository: TenantRepositoryPort,
    ) -> None:
        self._contact_repository = contact_repository
        self._tenant_repository = tenant_repository

    async def execute(self, input_dto: CreateContactInput) -> Contact:
        """Execute the CreateContact use case.

        Args:
            input_dto: Contact creation data

        Returns:
            Created Contact domain entity

        Raises:
            TenantNotFoundError: If tenant does not exist
            ContactPhoneAlreadyExistsError: If phone already registered in tenant
            ValueError: If name is empty or phone format invalid
        """
        tenant_id = TenantId.from_string(input_dto.tenant_id)

        if not await self._tenant_repository.exists(tenant_id):
            raise TenantNotFoundError(input_dto.tenant_id)

        phone_number = PhoneNumber.from_string(input_dto.phone_number)

        if await self._contact_repository.phone_exists_in_tenant(tenant_id, phone_number):
            raise ContactPhoneAlreadyExistsError(
                phone_number=phone_number.value,
                tenant_id=input_dto.tenant_id,
            )

        contact = Contact.create(
            tenant_id=tenant_id,
            phone_number=phone_number,
            name=input_dto.name,
            email=input_dto.email,
        )

        saved_contact = await self._contact_repository.save(contact)

        return saved_contact
