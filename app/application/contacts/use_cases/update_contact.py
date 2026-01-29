"""UpdateContact use case.

Updates an existing contact's information.

Invariants enforced:
- Contact must exist
- Contact name must not be empty (if provided)
"""

from app.application.contacts.dto import UpdateContactInput
from app.application.ports.repositories.contacts import ContactRepositoryPort
from app.domain.contacts.entities.contact import Contact
from app.domain.contacts.exceptions import ContactNotFoundError
from app.domain.contacts.value_objects.contact_id import ContactId


class UpdateContactUseCase:
    """Use case for updating an existing contact.

    Responsibilities:
    - Validate contact exists
    - Update allowed fields
    - Persist via repository

    Does NOT handle:
    - Phone number changes (requires uniqueness check, separate use case)
    - Authentication / authorization
    """

    def __init__(self, contact_repository: ContactRepositoryPort) -> None:
        self._contact_repository = contact_repository

    async def execute(self, input_dto: UpdateContactInput) -> Contact:
        """Execute the UpdateContact use case.

        Args:
            input_dto: Contact update data

        Returns:
            Updated Contact domain entity

        Raises:
            ContactNotFoundError: If contact does not exist
            ValueError: If name is empty
        """
        contact_id = ContactId.from_string(input_dto.contact_id)

        contact = await self._contact_repository.get_by_id(contact_id)
        if contact is None:
            raise ContactNotFoundError(input_dto.contact_id)

        if input_dto.name is not None:
            contact.rename(input_dto.name)

        if input_dto.email is not None:
            contact.update_email(input_dto.email)

        saved_contact = await self._contact_repository.save(contact)

        return saved_contact
