"""CancelBoleto use case.

Cancels an existing boleto.

Invariants enforced:
- Boleto must exist
- Boleto must not be already paid
- Boleto must not be already cancelled
- Requires explicit confirmation for monetary actions
- Boleto must be cancelled in Paytime before persisting
"""

from app.application.billing.dto import CancelBoletoInput
from app.application.ports.providers.paytime import (
    PaytimeCancelBoletoRequest,
    PaytimeProviderPort,
)
from app.application.ports.repositories.billing import BoletoRepositoryPort
from app.application.ports.repositories.collections import ReminderScheduleRepositoryPort
from app.domain.billing.entities.boleto import Boleto
from app.domain.billing.exceptions import BoletoNotFoundError, BoletoProviderError
from app.domain.billing.value_objects.boleto_id import BoletoId


class CancelBoletoUseCase:
    """Use case for cancelling a boleto.

    Requires explicit confirmation flag for monetary actions.
    Integrates with Paytime to cancel boleto in provider.
    Cancels pending reminders in Collections.
    """

    def __init__(
        self,
        boleto_repository: BoletoRepositoryPort,
        reminder_repository: ReminderScheduleRepositoryPort,
        paytime_provider: PaytimeProviderPort,
    ) -> None:
        self._boleto_repository = boleto_repository
        self._reminder_repository = reminder_repository
        self._paytime_provider = paytime_provider

    async def execute(self, input_dto: CancelBoletoInput) -> Boleto:
        """Execute the CancelBoleto use case.

        Args:
            input_dto: Boleto cancellation data

        Returns:
            Cancelled Boleto domain entity

        Raises:
            ValueError: If confirmed is False
            BoletoNotFoundError: If boleto does not exist
            BoletoAlreadyPaidError: If boleto is already paid
            BoletoAlreadyCancelledError: If boleto is already cancelled
            BoletoProviderError: If Paytime cancellation fails
        """
        if not input_dto.confirmed:
            raise ValueError(
                "Explicit confirmation required for monetary actions. "
                "Set confirmed=True to proceed."
            )

        boleto_id = BoletoId.from_string(input_dto.boleto_id)

        boleto = await self._boleto_repository.get_by_id(boleto_id)
        if boleto is None:
            raise BoletoNotFoundError(input_dto.boleto_id)

        if boleto.provider_reference:
            paytime_request = PaytimeCancelBoletoRequest(
                provider_boleto_id=boleto.provider_reference,
                reason=input_dto.reason,
            )

            paytime_response = await self._paytime_provider.cancel_boleto(paytime_request)

            if not paytime_response.success:
                raise BoletoProviderError(
                    paytime_response.error_message or "Unknown provider error"
                )

        boleto.cancel()

        await self._reminder_repository.cancel_for_boleto(boleto_id)

        saved_boleto = await self._boleto_repository.save(boleto)

        return saved_boleto
