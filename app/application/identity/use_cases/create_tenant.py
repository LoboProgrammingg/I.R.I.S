"""CreateTenant use case.

Creates a new tenant in the system.

Invariants enforced:
- Tenant name must not be empty (domain entity validation)
"""

from app.application.identity.dto import CreateTenantInput
from app.application.ports.repositories.identity import TenantRepositoryPort
from app.domain.identity.entities.tenant import Tenant


class CreateTenantUseCase:
    """Use case for creating a new tenant.

    Responsibilities:
    - Validate input
    - Create domain entity
    - Persist via repository

    Does NOT handle:
    - Authentication
    - Authorization
    - Messaging
    """

    def __init__(self, tenant_repository: TenantRepositoryPort) -> None:
        self._tenant_repository = tenant_repository

    async def execute(self, input_dto: CreateTenantInput) -> Tenant:
        """Execute the CreateTenant use case.

        Args:
            input_dto: Tenant creation data

        Returns:
            Created Tenant domain entity

        Raises:
            ValueError: If tenant name is empty (from domain)
        """
        tenant = Tenant.create(name=input_dto.name)

        saved_tenant = await self._tenant_repository.save(tenant)

        return saved_tenant
