"""QueueMessage use case.

Queues a message for delivery via the Outbox Pattern.

Invariants enforced:
- Tenant must exist
- Contact must exist and not be opted out
- Idempotency key must be unique per tenant
"""

from app.application.messaging.dto import QueueMessageInput
from app.application.ports.repositories.contacts import ContactRepositoryPort
from app.application.ports.repositories.identity import TenantRepositoryPort
from app.application.ports.repositories.messaging import OutboxRepositoryPort
from app.domain.contacts.value_objects.contact_id import ContactId
from app.domain.identity.exceptions import TenantNotFoundError
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.messaging.entities.outbox_item import MessageOutboxItem
from app.domain.messaging.exceptions import (
    ContactOptedOutError,
    DuplicateMessageError,
)
from app.domain.messaging.value_objects.message_type import MessageType
from app.domain.contacts.exceptions import ContactNotFoundError


class QueueMessageUseCase:
    """Use case for queuing a message in the outbox."""

    def __init__(
        self,
        outbox_repository: OutboxRepositoryPort,
        contact_repository: ContactRepositoryPort,
        tenant_repository: TenantRepositoryPort,
    ) -> None:
        self._outbox_repository = outbox_repository
        self._contact_repository = contact_repository
        self._tenant_repository = tenant_repository

    async def execute(self, input_dto: QueueMessageInput) -> MessageOutboxItem:
        """Execute the QueueMessage use case.

        Args:
            input_dto: Message queue data

        Returns:
            Created MessageOutboxItem

        Raises:
            TenantNotFoundError: If tenant does not exist
            ContactNotFoundError: If contact does not exist
            ContactOptedOutError: If contact has opted out
            DuplicateMessageError: If idempotency key exists
        """
        tenant_id = TenantId.from_string(input_dto.tenant_id)
        contact_id = ContactId.from_string(input_dto.contact_id)

        if not await self._tenant_repository.exists(tenant_id):
            raise TenantNotFoundError(input_dto.tenant_id)

        contact = await self._contact_repository.get_by_id(contact_id)
        if contact is None:
            raise ContactNotFoundError(input_dto.contact_id)

        if contact.opted_out:
            raise ContactOptedOutError(input_dto.contact_id)

        if await self._outbox_repository.exists_by_idempotency_key(
            tenant_id, input_dto.idempotency_key
        ):
            raise DuplicateMessageError(input_dto.idempotency_key, input_dto.tenant_id)

        message_type = MessageType(input_dto.message_type)

        item = MessageOutboxItem.create(
            tenant_id=tenant_id,
            contact_id=contact_id,
            message_type=message_type,
            payload=input_dto.payload,
            idempotency_key=input_dto.idempotency_key,
            scheduled_at=input_dto.scheduled_at,
        )

        saved_item = await self._outbox_repository.save(item)

        return saved_item
