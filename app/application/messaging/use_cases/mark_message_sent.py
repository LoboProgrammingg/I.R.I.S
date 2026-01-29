"""MarkMessageSent use case.

Marks a message outbox item as successfully sent.
"""

from app.application.messaging.dto import MarkMessageSentInput
from app.application.ports.repositories.messaging import OutboxRepositoryPort
from app.domain.messaging.entities.outbox_item import MessageOutboxItem
from app.domain.messaging.exceptions import MessageNotFoundError
from app.domain.messaging.value_objects.outbox_item_id import OutboxItemId


class MarkMessageSentUseCase:
    """Use case for marking a message as sent."""

    def __init__(self, outbox_repository: OutboxRepositoryPort) -> None:
        self._outbox_repository = outbox_repository

    async def execute(self, input_dto: MarkMessageSentInput) -> MessageOutboxItem:
        """Execute the MarkMessageSent use case.

        Args:
            input_dto: Message sent data

        Returns:
            Updated MessageOutboxItem

        Raises:
            MessageNotFoundError: If message does not exist
        """
        item_id = OutboxItemId.from_string(input_dto.item_id)

        item = await self._outbox_repository.get_by_id(item_id)
        if item is None:
            raise MessageNotFoundError(input_dto.item_id)

        item.mark_as_sent()

        saved_item = await self._outbox_repository.save(item)

        return saved_item
