"""GetBoletoStatus use case.

Retrieves the current status of a boleto.
"""

from app.application.billing.dto import GetBoletoStatusInput
from app.application.ports.repositories.billing import BoletoRepositoryPort
from app.domain.billing.entities.boleto import Boleto
from app.domain.billing.exceptions import BoletoNotFoundError
from app.domain.billing.value_objects.boleto_id import BoletoId


class GetBoletoStatusUseCase:
    """Use case for retrieving boleto status."""

    def __init__(self, boleto_repository: BoletoRepositoryPort) -> None:
        self._boleto_repository = boleto_repository

    async def execute(self, input_dto: GetBoletoStatusInput) -> Boleto:
        """Execute the GetBoletoStatus use case.

        Args:
            input_dto: Boleto lookup data

        Returns:
            Boleto domain entity

        Raises:
            BoletoNotFoundError: If boleto does not exist
        """
        boleto_id = BoletoId.from_string(input_dto.boleto_id)

        boleto = await self._boleto_repository.get_by_id(boleto_id)
        if boleto is None:
            raise BoletoNotFoundError(input_dto.boleto_id)

        return boleto
