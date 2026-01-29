"""OptOutContact use case.

Manages contact messaging opt-out preference.

Invariants enforced:
- Contact must exist
- Opted-out contacts cannot receive marketing messages
"""

from app.application.contacts.dto import OptOutContactInput
from app.application.ports.repositories.contacts import ContactRepositoryPort
from app.domain.contacts.entities.contact import Contact
from app.domain.contacts.exceptions import ContactNotFoundError
from app.domain.contacts.value_objects.contact_id import ContactId


class OptOutContactUseCase:
    """Use case for managing contact opt-out preference.

    Responsibilities:
    - Validate contact exists
    - Update opt-out status
    - Persist via repository

    Does NOT handle:
    - Stopping in-flight messages (Messaging context)
    - Audit logging (future)
    """

    def __init__(self, contact_repository: ContactRepositoryPort) -> None:
        self._contact_repository = contact_repository

    async def execute(self, input_dto: OptOutContactInput) -> Contact:
        """Execute the OptOutContact use case.

        Args:
            input_dto: Opt-out preference data

        Returns:
            Updated Contact domain entity

        Raises:
            ContactNotFoundError: If contact does not exist
        """
        contact_id = ContactId.from_string(input_dto.contact_id)

        contact = await self._contact_repository.get_by_id(contact_id)
        if contact is None:
            raise ContactNotFoundError(input_dto.contact_id)

        if input_dto.opt_out:
            contact.opt_out()
        else:
            contact.opt_in()

        saved_contact = await self._contact_repository.save(contact)

        return saved_contact
