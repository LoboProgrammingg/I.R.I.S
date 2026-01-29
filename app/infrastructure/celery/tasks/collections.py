"""Celery tasks for Collections bounded context.

Implements scheduled jobs for overdue detection, interest application,
and reminder scheduling.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from celery import shared_task
from sqlalchemy import select, update

from app.config.logging import get_logger
from app.domain.billing.value_objects.boleto_status import BoletoStatus
from app.infrastructure.db.models.billing import BoletoModel
from app.infrastructure.db.models.collections import (
    InterestPolicyModel,
    ReminderScheduleModel,
)
from app.infrastructure.db.repositories.collections import (
    InterestPolicyRepository,
    ReminderScheduleRepository,
)
from app.infrastructure.db.repositories.messaging import OutboxRepository
from app.domain.messaging.entities.outbox_item import MessageOutboxItem
from app.domain.messaging.value_objects.message_type import MessageType
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.contacts.value_objects.contact_id import ContactId


logger = get_logger("collections_tasks")


@shared_task(
    name="collections.mark_overdue_boletos",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def mark_overdue_boletos(self, batch_size: int = 100) -> dict:
    """Mark SENT boletos as OVERDUE when due date has passed.

    Idempotency: Safe to run multiple times - only marks SENT boletos.
    """
    return asyncio.get_event_loop().run_until_complete(
        _mark_overdue_async(batch_size)
    )


async def _mark_overdue_async(batch_size: int) -> dict:
    """Async implementation of mark_overdue."""
    from app.infrastructure.db.session import async_session_factory

    marked_count = 0
    now = datetime.now(timezone.utc)

    async with async_session_factory() as session:
        result = await session.execute(
            select(BoletoModel)
            .where(
                BoletoModel.status == "sent",
                BoletoModel.due_date < now,
            )
            .limit(batch_size)
        )
        boletos = result.scalars().all()

        for boleto in boletos:
            boleto.status = "overdue"
            boleto.updated_at = now
            marked_count += 1

        await session.commit()

    summary = {
        "processed": len(boletos) if boletos else 0,
        "marked_overdue": marked_count,
        "timestamp": now.isoformat(),
    }

    logger.info("mark_overdue_complete", **summary)
    return summary


@shared_task(
    name="collections.apply_interest",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def apply_interest(self, batch_size: int = 100) -> dict:
    """Apply interest to overdue boletos based on tenant policy.

    Idempotency: Tracks applied interest per boleto (future: audit table).
    MVP: Logs interest calculation but does not modify boleto amount.
    """
    return asyncio.get_event_loop().run_until_complete(
        _apply_interest_async(batch_size)
    )


async def _apply_interest_async(batch_size: int) -> dict:
    """Async implementation of apply_interest."""
    from app.infrastructure.db.session import async_session_factory

    processed = 0
    total_interest = 0
    now = datetime.now(timezone.utc)

    async with async_session_factory() as session:
        result = await session.execute(
            select(BoletoModel)
            .where(BoletoModel.status == "overdue")
            .limit(batch_size)
        )
        boletos = result.scalars().all()

        for boleto in boletos:
            policy_result = await session.execute(
                select(InterestPolicyModel).where(
                    InterestPolicyModel.tenant_id == boleto.tenant_id,
                    InterestPolicyModel.is_active == True,
                )
            )
            policy = policy_result.scalar_one_or_none()

            if policy is None:
                continue

            days_overdue = (now.date() - boleto.due_date.date()).days
            if days_overdue <= policy.grace_period_days:
                continue

            effective_days = days_overdue - policy.grace_period_days
            daily_rate = policy.daily_interest_rate_bps / 10000
            interest = int(boleto.amount_cents * daily_rate * effective_days)
            interest += policy.fixed_penalty_cents

            total_interest += interest
            processed += 1

            logger.info(
                "interest_calculated",
                boleto_id=str(boleto.id),
                principal=boleto.amount_cents,
                days_overdue=days_overdue,
                interest=interest,
            )

        await session.commit()

    summary = {
        "processed": processed,
        "total_interest_cents": total_interest,
        "timestamp": now.isoformat(),
    }

    logger.info("apply_interest_complete", **summary)
    return summary


@shared_task(
    name="collections.schedule_reminders",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def schedule_reminders(self, batch_size: int = 50) -> dict:
    """Process pending reminders and queue them via Messaging.

    Idempotency: Uses reminder schedule status to track sent reminders.
    """
    return asyncio.get_event_loop().run_until_complete(
        _schedule_reminders_async(batch_size)
    )


async def _schedule_reminders_async(batch_size: int) -> dict:
    """Async implementation of schedule_reminders."""
    from app.infrastructure.db.session import async_session_factory
    from app.infrastructure.db.repositories.contacts import ContactRepository

    sent_count = 0
    skipped_count = 0
    now = datetime.now(timezone.utc)

    async with async_session_factory() as session:
        reminder_repo = ReminderScheduleRepository(session)
        outbox_repo = OutboxRepository(session)
        contact_repo = ContactRepository(session)

        pending = await reminder_repo.get_pending(limit=batch_size)

        for schedule in pending:
            boleto_result = await session.execute(
                select(BoletoModel).where(BoletoModel.id == schedule.boleto_id.value)
            )
            boleto = boleto_result.scalar_one_or_none()

            if boleto is None or boleto.status in ("paid", "cancelled"):
                schedule.cancel()
                await reminder_repo.save(schedule)
                skipped_count += 1
                continue

            contact = await contact_repo.get_by_id(schedule.boleto_id)
            if contact is None or contact.opted_out:
                schedule.cancel()
                await reminder_repo.save(schedule)
                skipped_count += 1
                continue

            outbox_item = MessageOutboxItem.create(
                tenant_id=schedule.tenant_id,
                contact_id=ContactId(value=boleto.contact_id),
                message_type=MessageType.REMINDER,
                payload={
                    "boleto_id": str(schedule.boleto_id),
                    "amount_cents": boleto.amount_cents,
                    "due_date": boleto.due_date.isoformat(),
                },
                idempotency_key=f"reminder_{schedule.id}_{schedule.attempt_count}",
            )

            await outbox_repo.save(outbox_item)

            schedule.mark_as_sent()
            await reminder_repo.save(schedule)
            sent_count += 1

        await session.commit()

    summary = {
        "processed": len(pending),
        "sent": sent_count,
        "skipped": skipped_count,
        "timestamp": now.isoformat(),
    }

    logger.info("schedule_reminders_complete", **summary)
    return summary
