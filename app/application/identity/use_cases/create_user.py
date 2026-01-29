"""CreateUser use case.

Creates a new user within a tenant.

Invariants enforced:
- User name must not be empty (domain entity validation)
- Phone number must be valid E.164 (PhoneNumber value object)
- Phone number must be unique within tenant (repository check)
- Tenant must exist (repository check)
- User role must be valid (UserRole enum)
"""

from app.application.identity.dto import CreateUserInput
from app.application.ports.repositories.identity import (
    TenantRepositoryPort,
    UserRepositoryPort,
)
from app.domain.identity.entities.user import User
from app.domain.identity.exceptions import (
    PhoneAlreadyRegisteredError,
    TenantNotFoundError,
)
from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.identity.value_objects.user_role import UserRole


class CreateUserUseCase:
    """Use case for creating a new user within a tenant.

    Responsibilities:
    - Validate tenant exists
    - Validate phone uniqueness within tenant
    - Create domain entity with validated value objects
    - Persist via repository

    Does NOT handle:
    - Authentication
    - Authorization
    - Messaging / notifications
    - Welcome emails
    """

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        tenant_repository: TenantRepositoryPort,
    ) -> None:
        self._user_repository = user_repository
        self._tenant_repository = tenant_repository

    async def execute(self, input_dto: CreateUserInput) -> User:
        """Execute the CreateUser use case.

        Args:
            input_dto: User creation data

        Returns:
            Created User domain entity

        Raises:
            TenantNotFoundError: If tenant does not exist
            PhoneAlreadyRegisteredError: If phone already registered in tenant
            ValueError: If name is empty or phone format invalid
        """
        tenant_id = TenantId.from_string(input_dto.tenant_id)

        if not await self._tenant_repository.exists(tenant_id):
            raise TenantNotFoundError(input_dto.tenant_id)

        phone_number = PhoneNumber.from_string(input_dto.phone_number)

        if await self._user_repository.phone_exists_in_tenant(tenant_id, phone_number):
            raise PhoneAlreadyRegisteredError(
                phone_number=phone_number.value,
                tenant_id=input_dto.tenant_id,
            )

        role = UserRole(input_dto.role)

        user = User.create(
            tenant_id=tenant_id,
            phone_number=phone_number,
            name=input_dto.name,
            role=role,
        )

        saved_user = await self._user_repository.save(user)

        return saved_user
