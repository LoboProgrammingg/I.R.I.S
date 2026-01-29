"""Dependencies for Billing endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.billing.use_cases.cancel_boleto import CancelBoletoUseCase
from app.application.billing.use_cases.create_boleto import CreateBoletoUseCase
from app.application.billing.use_cases.get_boleto_status import GetBoletoStatusUseCase
from app.infrastructure.db.repositories.billing import BoletoRepository
from app.infrastructure.db.repositories.contacts import ContactRepository
from app.infrastructure.db.repositories.identity import TenantRepository
from app.infrastructure.db.session import get_session


async def get_create_boleto_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateBoletoUseCase:
    """Provide CreateBoletoUseCase with dependencies."""
    boleto_repo = BoletoRepository(session)
    contact_repo = ContactRepository(session)
    tenant_repo = TenantRepository(session)
    return CreateBoletoUseCase(
        boleto_repository=boleto_repo,
        contact_repository=contact_repo,
        tenant_repository=tenant_repo,
    )


async def get_cancel_boleto_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CancelBoletoUseCase:
    """Provide CancelBoletoUseCase with dependencies."""
    boleto_repo = BoletoRepository(session)
    return CancelBoletoUseCase(boleto_repository=boleto_repo)


async def get_get_boleto_status_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetBoletoStatusUseCase:
    """Provide GetBoletoStatusUseCase with dependencies."""
    boleto_repo = BoletoRepository(session)
    return GetBoletoStatusUseCase(boleto_repository=boleto_repo)
