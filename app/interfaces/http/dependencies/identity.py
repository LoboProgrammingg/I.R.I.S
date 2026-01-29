"""Dependencies for Identity & Tenancy endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.identity.use_cases.create_tenant import CreateTenantUseCase
from app.application.identity.use_cases.create_user import CreateUserUseCase
from app.infrastructure.db.repositories.identity import TenantRepository, UserRepository
from app.infrastructure.db.session import get_session


async def get_create_tenant_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateTenantUseCase:
    """Provide CreateTenantUseCase with dependencies."""
    tenant_repo = TenantRepository(session)
    return CreateTenantUseCase(tenant_repository=tenant_repo)


async def get_create_user_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateUserUseCase:
    """Provide CreateUserUseCase with dependencies."""
    tenant_repo = TenantRepository(session)
    user_repo = UserRepository(session)
    return CreateUserUseCase(
        user_repository=user_repo,
        tenant_repository=tenant_repo,
    )
