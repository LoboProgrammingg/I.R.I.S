"""MarkMessageFailed use case.

Marks a message outbox item as failed, with optional retry.
"""

from app.application.messaging.dto import MarkMessageFailedInput
from app.application.ports.repositories.messaging import OutboxRepositoryPort
from app.domain.messaging.entities.outbox_item import MessageOutboxItem
from app.domain.messaging.exceptions import MessageNotFoundError
from app.domain.messaging.value_objects.outbox_item_id import OutboxItemId


MAX_RETRY_ATTEMPTS = 5


class MarkMessageFailedUseCase:
    """Use case for marking a message as failed."""

    def __init__(self, outbox_repository: OutboxRepositoryPort) -> None:
        self._outbox_repository = outbox_repository

    async def execute(self, input_dto: MarkMessageFailedInput) -> MessageOutboxItem:
        """Execute the MarkMessageFailed use case.

        Args:
            input_dto: Message failure data

        Returns:
            Updated MessageOutboxItem

        Raises:
            MessageNotFoundError: If message does not exist
        """
        item_id = OutboxItemId.from_string(input_dto.item_id)

        item = await self._outbox_repository.get_by_id(item_id)
        if item is None:
            raise MessageNotFoundError(input_dto.item_id)

        if input_dto.should_retry and item.attempt_count < MAX_RETRY_ATTEMPTS:
            item.mark_for_retry(input_dto.error)
        else:
            item.mark_as_failed(input_dto.error)

        saved_item = await self._outbox_repository.save(item)

        return saved_item
