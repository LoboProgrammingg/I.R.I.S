"""Dependencies for Contacts endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.contacts.use_cases.create_contact import CreateContactUseCase
from app.application.contacts.use_cases.opt_out_contact import OptOutContactUseCase
from app.application.contacts.use_cases.update_contact import UpdateContactUseCase
from app.infrastructure.db.repositories.contacts import ContactRepository
from app.infrastructure.db.repositories.identity import TenantRepository
from app.infrastructure.db.session import get_session


async def get_create_contact_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateContactUseCase:
    """Provide CreateContactUseCase with dependencies."""
    contact_repo = ContactRepository(session)
    tenant_repo = TenantRepository(session)
    return CreateContactUseCase(
        contact_repository=contact_repo,
        tenant_repository=tenant_repo,
    )


async def get_update_contact_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdateContactUseCase:
    """Provide UpdateContactUseCase with dependencies."""
    contact_repo = ContactRepository(session)
    return UpdateContactUseCase(contact_repository=contact_repo)


async def get_opt_out_contact_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OptOutContactUseCase:
    """Provide OptOutContactUseCase with dependencies."""
    contact_repo = ContactRepository(session)
    return OptOutContactUseCase(contact_repository=contact_repo)
