"""Repository implementations for Identity & Tenancy bounded context.

Maps domain entities to SQLAlchemy models and implements persistence operations.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories.identity import (
    TenantRepositoryPort,
    UserRepositoryPort,
)
from app.domain.identity.entities.tenant import Tenant
from app.domain.identity.entities.user import User
from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.identity.value_objects.user_id import UserId
from app.domain.identity.value_objects.user_role import UserRole
from app.infrastructure.db.models.identity import TenantModel, UserModel


class TenantRepository(TenantRepositoryPort):
    """SQLAlchemy implementation of TenantRepositoryPort."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, tenant_id: TenantId) -> Tenant | None:
        """Retrieve a tenant by its ID."""
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.id == tenant_id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def save(self, tenant: Tenant) -> Tenant:
        """Persist a tenant (create or update)."""
        existing = await self._session.get(TenantModel, tenant.id.value)

        if existing is None:
            model = self._to_model(tenant)
            self._session.add(model)
        else:
            existing.name = tenant.name
            existing.is_active = tenant.is_active
            existing.updated_at = tenant.updated_at
            model = existing

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def exists(self, tenant_id: TenantId) -> bool:
        """Check if a tenant exists."""
        result = await self._session.execute(
            select(TenantModel.id).where(TenantModel.id == tenant_id.value)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_domain(model: TenantModel) -> Tenant:
        """Map SQLAlchemy model to domain entity."""
        return Tenant(
            id=TenantId(value=model.id),
            name=model.name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(tenant: Tenant) -> TenantModel:
        """Map domain entity to SQLAlchemy model."""
        return TenantModel(
            id=tenant.id.value,
            name=tenant.name,
            is_active=tenant.is_active,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )


class UserRepository(UserRepositoryPort):
    """SQLAlchemy implementation of UserRepositoryPort."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UserId) -> User | None:
        """Retrieve a user by its ID."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_phone(
        self, tenant_id: TenantId, phone_number: PhoneNumber
    ) -> User | None:
        """Retrieve a user by phone number within a tenant."""
        result = await self._session.execute(
            select(UserModel).where(
                UserModel.tenant_id == tenant_id.value,
                UserModel.phone_number == phone_number.value,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def save(self, user: User) -> User:
        """Persist a user (create or update)."""
        existing = await self._session.get(UserModel, user.id.value)

        if existing is None:
            model = self._to_model(user)
            self._session.add(model)
        else:
            existing.name = user.name
            existing.phone_number = user.phone_number.value
            existing.role = user.role.value
            existing.is_active = user.is_active
            existing.updated_at = user.updated_at
            model = existing

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def list_by_tenant(self, tenant_id: TenantId) -> list[User]:
        """List all users in a tenant."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.tenant_id == tenant_id.value)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def phone_exists_in_tenant(
        self, tenant_id: TenantId, phone_number: PhoneNumber
    ) -> bool:
        """Check if a phone number is already registered in a tenant."""
        result = await self._session.execute(
            select(UserModel.id).where(
                UserModel.tenant_id == tenant_id.value,
                UserModel.phone_number == phone_number.value,
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        """Map SQLAlchemy model to domain entity."""
        return User(
            id=UserId(value=model.id),
            tenant_id=TenantId(value=model.tenant_id),
            phone_number=PhoneNumber(value=model.phone_number),
            name=model.name,
            role=UserRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(user: User) -> UserModel:
        """Map domain entity to SQLAlchemy model."""
        return UserModel(
            id=user.id.value,
            tenant_id=user.tenant_id.value,
            phone_number=user.phone_number.value,
            name=user.name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
