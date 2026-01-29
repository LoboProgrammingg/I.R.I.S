"""Celery tasks for Messaging bounded context.

Implements the Outbox Pattern delivery worker.
"""

import asyncio
from datetime import datetime, timezone

from celery import shared_task

from app.config.logging import get_logger
from app.infrastructure.db.repositories.contacts import ContactRepository
from app.infrastructure.db.repositories.messaging import OutboxRepository
from app.infrastructure.db.session import get_sync_session
from app.infrastructure.providers.messaging_stub import StubMessagingProvider


logger = get_logger("messaging_tasks")


MAX_BATCH_SIZE = 50
MAX_RETRIES = 5
RETRY_BACKOFF_SECONDS = [60, 300, 900, 3600, 7200]


@shared_task(
    name="messaging.deliver_outbox_messages",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def deliver_outbox_messages(self, batch_size: int = MAX_BATCH_SIZE) -> dict:
    """Deliver pending messages from the outbox.

    Fetches pending items and delivers them using the messaging provider.
    Respects opt-out preferences and retry logic.

    Args:
        batch_size: Maximum number of messages to process

    Returns:
        Summary of processed messages
    """
    return asyncio.get_event_loop().run_until_complete(
        _deliver_outbox_messages_async(batch_size)
    )


async def _deliver_outbox_messages_async(batch_size: int) -> dict:
    """Async implementation of outbox delivery."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.infrastructure.db.session import async_session_factory

    sent_count = 0
    failed_count = 0
    skipped_count = 0

    async with async_session_factory() as session:
        outbox_repo = OutboxRepository(session)
        contact_repo = ContactRepository(session)
        provider = StubMessagingProvider()

        pending_items = await outbox_repo.get_pending(limit=batch_size)

        logger.info(
            "processing_outbox_batch",
            pending_count=len(pending_items),
            batch_size=batch_size,
        )

        for item in pending_items:
            try:
                contact = await contact_repo.get_by_id(item.contact_id)

                if contact is None or contact.opted_out:
                    logger.info(
                        "skipping_opted_out_contact",
                        item_id=str(item.id),
                        contact_id=str(item.contact_id),
                    )
                    item.mark_as_failed("Contact opted out or not found")
                    await outbox_repo.save(item)
                    skipped_count += 1
                    continue

                item.increment_attempt()

                result = await provider.send(
                    recipient_phone=contact.phone_number.value,
                    message_type=item.message_type.value,
                    payload=item.payload,
                )

                if result.success:
                    item.mark_as_sent()
                    await outbox_repo.save(item)
                    sent_count += 1
                    logger.info(
                        "message_sent",
                        item_id=str(item.id),
                        provider_message_id=result.provider_message_id,
                    )
                else:
                    if item.attempt_count < MAX_RETRIES:
                        item.mark_for_retry(result.error or "Unknown error")
                    else:
                        item.mark_as_failed(result.error or "Max retries exceeded")
                    await outbox_repo.save(item)
                    failed_count += 1
                    logger.warning(
                        "message_delivery_failed",
                        item_id=str(item.id),
                        attempt=item.attempt_count,
                        error=result.error,
                    )

            except Exception as e:
                logger.exception(
                    "message_delivery_error",
                    item_id=str(item.id),
                    error=str(e),
                )
                if item.attempt_count < MAX_RETRIES:
                    item.mark_for_retry(str(e))
                else:
                    item.mark_as_failed(str(e))
                await outbox_repo.save(item)
                failed_count += 1

        await session.commit()

    summary = {
        "processed": len(pending_items),
        "sent": sent_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    logger.info("outbox_batch_complete", **summary)

    return summary
