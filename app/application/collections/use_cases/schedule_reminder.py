"""ScheduleReminder use case.

Schedules a reminder for an unpaid boleto.
"""

from app.application.collections.dto import ScheduleReminderInput
from app.application.ports.repositories.billing import BoletoRepositoryPort
from app.application.ports.repositories.collections import ReminderScheduleRepositoryPort
from app.domain.billing.exceptions import BoletoNotFoundError
from app.domain.billing.value_objects.boleto_id import BoletoId
from app.domain.collections.entities.reminder_schedule import ReminderSchedule
from app.domain.identity.value_objects.tenant_id import TenantId


class ScheduleReminderUseCase:
    """Use case for scheduling a reminder for a boleto."""

    def __init__(
        self,
        reminder_repository: ReminderScheduleRepositoryPort,
        boleto_repository: BoletoRepositoryPort,
    ) -> None:
        self._reminder_repository = reminder_repository
        self._boleto_repository = boleto_repository

    async def execute(self, input_dto: ScheduleReminderInput) -> ReminderSchedule:
        """Execute the ScheduleReminder use case.

        Raises:
            BoletoNotFoundError: If boleto does not exist
        """
        tenant_id = TenantId.from_string(input_dto.tenant_id)
        boleto_id = BoletoId.from_string(input_dto.boleto_id)

        boleto = await self._boleto_repository.get_by_id(boleto_id)
        if boleto is None:
            raise BoletoNotFoundError(input_dto.boleto_id)

        if boleto.is_paid() or boleto.is_cancelled():
            await self._reminder_repository.cancel_for_boleto(boleto_id)
            raise ValueError("Cannot schedule reminder for paid or cancelled boleto")

        schedule = ReminderSchedule.create(
            tenant_id=tenant_id,
            boleto_id=boleto_id,
            scheduled_at=input_dto.scheduled_at,
        )

        saved_schedule = await self._reminder_repository.save(schedule)

        return saved_schedule
