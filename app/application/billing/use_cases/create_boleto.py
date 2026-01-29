"""CreateBoleto use case.

Creates a new boleto for a contact within a tenant.

Invariants enforced:
- Tenant must exist
- Contact must exist
- Amount must be positive
- Due date must be valid
- Idempotency key must be unique per tenant
- Requires explicit confirmation for monetary actions
- Boleto must be created in Paytime before persisting
"""

from app.application.billing.dto import CreateBoletoInput
from app.application.ports.providers.paytime import (
    PaytimeCreateBoletoRequest,
    PaytimeProviderPort,
)
from app.application.ports.repositories.billing import BoletoRepositoryPort
from app.application.ports.repositories.contacts import ContactRepositoryPort
from app.application.ports.repositories.identity import TenantRepositoryPort
from app.domain.billing.entities.boleto import Boleto
from app.domain.billing.exceptions import (
    BoletoProviderError,
    DuplicateBoletoError,
)
from app.domain.billing.value_objects.due_date import DueDate
from app.domain.billing.value_objects.money import Money
from app.domain.contacts.exceptions import ContactNotFoundError
from app.domain.contacts.value_objects.contact_id import ContactId
from app.domain.identity.exceptions import TenantNotFoundError
from app.domain.identity.value_objects.tenant_id import TenantId


class CreateBoletoUseCase:
    """Use case for creating a new boleto.

    Requires explicit confirmation flag for monetary actions.
    Integrates with Paytime to create boleto in provider.
    """

    def __init__(
        self,
        boleto_repository: BoletoRepositoryPort,
        contact_repository: ContactRepositoryPort,
        tenant_repository: TenantRepositoryPort,
        paytime_provider: PaytimeProviderPort,
    ) -> None:
        self._boleto_repository = boleto_repository
        self._contact_repository = contact_repository
        self._tenant_repository = tenant_repository
        self._paytime_provider = paytime_provider

    async def execute(self, input_dto: CreateBoletoInput) -> Boleto:
        """Execute the CreateBoleto use case.

        Args:
            input_dto: Boleto creation data

        Returns:
            Created Boleto domain entity with provider_reference

        Raises:
            ValueError: If confirmed is False (explicit confirmation required)
            TenantNotFoundError: If tenant does not exist
            ContactNotFoundError: If contact does not exist
            DuplicateBoletoError: If idempotency key already exists
            BoletoProviderError: If Paytime creation fails
        """
        if not input_dto.confirmed:
            raise ValueError(
                "Explicit confirmation required for monetary actions. "
                "Set confirmed=True to proceed."
            )

        tenant_id = TenantId.from_string(input_dto.tenant_id)
        contact_id = ContactId.from_string(input_dto.contact_id)

        if not await self._tenant_repository.exists(tenant_id):
            raise TenantNotFoundError(input_dto.tenant_id)

        contact = await self._contact_repository.get_by_id(contact_id)
        if contact is None:
            raise ContactNotFoundError(input_dto.contact_id)

        if contact.tenant_id != tenant_id:
            raise ContactNotFoundError(input_dto.contact_id)

        if await self._boleto_repository.exists_by_idempotency_key(
            tenant_id, input_dto.idempotency_key
        ):
            raise DuplicateBoletoError(input_dto.idempotency_key, input_dto.tenant_id)

        amount = Money(amount_cents=input_dto.amount_cents)
        due_date = DueDate.from_string(input_dto.due_date)

        paytime_request = PaytimeCreateBoletoRequest(
            amount_cents=amount.amount_cents,
            due_date=due_date.to_iso_string(),
            payer_name=contact.name,
            payer_phone=contact.phone_number,
            idempotency_key=input_dto.idempotency_key,
        )

        paytime_response = await self._paytime_provider.create_boleto(paytime_request)

        if not paytime_response.success:
            raise BoletoProviderError(
                paytime_response.error_message or "Unknown provider error"
            )

        boleto = Boleto.create(
            tenant_id=tenant_id,
            contact_id=contact_id,
            amount=amount,
            due_date=due_date,
            idempotency_key=input_dto.idempotency_key,
        )

        boleto.mark_as_sent(paytime_response.provider_boleto_id)

        saved_boleto = await self._boleto_repository.save(boleto)

        return saved_boleto
