"""Repository implementation for Contacts bounded context.

Maps domain entities to SQLAlchemy models and implements persistence operations.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories.contacts import ContactRepositoryPort
from app.domain.contacts.entities.contact import Contact
from app.domain.contacts.value_objects.contact_id import ContactId
from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId
from app.infrastructure.db.models.contacts import ContactModel


class ContactRepository(ContactRepositoryPort):
    """SQLAlchemy implementation of ContactRepositoryPort."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, contact_id: ContactId) -> Contact | None:
        """Retrieve a contact by its ID."""
        result = await self._session.execute(
            select(ContactModel).where(ContactModel.id == contact_id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_phone(
        self, tenant_id: TenantId, phone_number: PhoneNumber
    ) -> Contact | None:
        """Retrieve a contact by phone number within a tenant."""
        result = await self._session.execute(
            select(ContactModel).where(
                ContactModel.tenant_id == tenant_id.value,
                ContactModel.phone_number == phone_number.value,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def save(self, contact: Contact) -> Contact:
        """Persist a contact (create or update)."""
        existing = await self._session.get(ContactModel, contact.id.value)

        if existing is None:
            model = self._to_model(contact)
            self._session.add(model)
        else:
            existing.name = contact.name
            existing.phone_number = contact.phone_number.value
            existing.email = contact.email
            existing.is_active = contact.is_active
            existing.opted_out = contact.opted_out
            existing.updated_at = contact.updated_at
            model = existing

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def list_by_tenant(self, tenant_id: TenantId) -> list[Contact]:
        """List all contacts in a tenant."""
        result = await self._session.execute(
            select(ContactModel).where(ContactModel.tenant_id == tenant_id.value)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def phone_exists_in_tenant(
        self, tenant_id: TenantId, phone_number: PhoneNumber
    ) -> bool:
        """Check if a phone number is already registered in a tenant."""
        result = await self._session.execute(
            select(ContactModel.id).where(
                ContactModel.tenant_id == tenant_id.value,
                ContactModel.phone_number == phone_number.value,
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_domain(model: ContactModel) -> Contact:
        """Map SQLAlchemy model to domain entity."""
        return Contact(
            id=ContactId(value=model.id),
            tenant_id=TenantId(value=model.tenant_id),
            phone_number=PhoneNumber(value=model.phone_number),
            name=model.name,
            email=model.email,
            is_active=model.is_active,
            opted_out=model.opted_out,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(contact: Contact) -> ContactModel:
        """Map domain entity to SQLAlchemy model."""
        return ContactModel(
            id=contact.id.value,
            tenant_id=contact.tenant_id.value,
            phone_number=contact.phone_number.value,
            name=contact.name,
            email=contact.email,
            is_active=contact.is_active,
            opted_out=contact.opted_out,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
        )
