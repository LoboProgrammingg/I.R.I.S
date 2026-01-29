"""Repository ports for Billing bounded context."""

from abc import ABC, abstractmethod

from app.domain.billing.entities.boleto import Boleto
from app.domain.billing.entities.payment import Payment
from app.domain.billing.value_objects.boleto_id import BoletoId
from app.domain.identity.value_objects.tenant_id import TenantId


class BoletoRepositoryPort(ABC):
    """Port for Boleto persistence operations."""

    @abstractmethod
    async def get_by_id(self, boleto_id: BoletoId) -> Boleto | None:
        """Retrieve a boleto by its ID."""
        ...

    @abstractmethod
    async def get_by_provider_reference(self, provider_reference: str) -> Boleto | None:
        """Retrieve a boleto by its Paytime provider reference."""
        ...

    @abstractmethod
    async def save(self, boleto: Boleto) -> Boleto:
        """Persist a boleto (create or update)."""
        ...

    @abstractmethod
    async def exists_by_idempotency_key(
        self, tenant_id: TenantId, idempotency_key: str
    ) -> bool:
        """Check if a boleto with given idempotency key exists in tenant."""
        ...


class PaymentRepositoryPort(ABC):
    """Port for Payment persistence operations."""

    @abstractmethod
    async def get_by_boleto_id(self, boleto_id: BoletoId) -> Payment | None:
        """Retrieve payment for a boleto."""
        ...

    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        """Retrieve payment by idempotency key."""
        ...

    @abstractmethod
    async def save(self, payment: Payment) -> Payment:
        """Persist a payment."""
        ...
