"""CreateInterestPolicy use case."""

from app.application.collections.dto import CreateInterestPolicyInput
from app.application.ports.repositories.collections import InterestPolicyRepositoryPort
from app.application.ports.repositories.identity import TenantRepositoryPort
from app.domain.collections.entities.interest_policy import InterestPolicy
from app.domain.identity.exceptions import TenantNotFoundError
from app.domain.identity.value_objects.tenant_id import TenantId


class CreateInterestPolicyUseCase:
    """Use case for creating or updating interest policy for a tenant."""

    def __init__(
        self,
        policy_repository: InterestPolicyRepositoryPort,
        tenant_repository: TenantRepositoryPort,
    ) -> None:
        self._policy_repository = policy_repository
        self._tenant_repository = tenant_repository

    async def execute(self, input_dto: CreateInterestPolicyInput) -> InterestPolicy:
        """Execute the CreateInterestPolicy use case.

        If an active policy exists, it will be deactivated and replaced.
        """
        tenant_id = TenantId.from_string(input_dto.tenant_id)

        if not await self._tenant_repository.exists(tenant_id):
            raise TenantNotFoundError(input_dto.tenant_id)

        existing = await self._policy_repository.get_by_tenant(tenant_id)
        if existing is not None:
            existing.deactivate()
            await self._policy_repository.save(existing)

        policy = InterestPolicy.create(
            tenant_id=tenant_id,
            grace_period_days=input_dto.grace_period_days,
            daily_interest_rate_bps=input_dto.daily_interest_rate_bps,
            fixed_penalty_cents=input_dto.fixed_penalty_cents,
        )

        saved_policy = await self._policy_repository.save(policy)

        return saved_policy
