"""Contact aggregate root."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.contacts.value_objects.contact_id import ContactId
from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId


@dataclass
class Contact:
    """Contact aggregate root.

    Represents a person or entity that can receive boletos and messages.
    Contacts are scoped to exactly one tenant.

    Invariants:
    - Contact must belong to exactly one tenant
    - Phone number must be unique within a tenant (enforced by repository)
    - Phone number must be valid E.164 format (enforced by PhoneNumber VO)
    - Contact name must not be empty
    - Contact ID is immutable after creation
    - Opted-out contacts cannot receive marketing messages
    """

    id: ContactId
    tenant_id: TenantId
    phone_number: PhoneNumber
    name: str
    email: str | None = None
    is_active: bool = True
    opted_out: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate contact invariants."""
        if not self.name or not self.name.strip():
            raise ValueError("Contact name must not be empty")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        phone_number: PhoneNumber,
        name: str,
        email: str | None = None,
        contact_id: ContactId | None = None,
    ) -> "Contact":
        """Factory method to create a new Contact.

        Args:
            tenant_id: Owning tenant
            phone_number: E.164 normalized phone
            name: Contact display name
            email: Optional email address
            contact_id: Optional pre-generated ID

        Returns:
            New Contact instance
        """
        return cls(
            id=contact_id or ContactId.generate(),
            tenant_id=tenant_id,
            phone_number=phone_number,
            name=name.strip(),
            email=email.strip() if email else None,
            is_active=True,
            opted_out=False,
        )

    def deactivate(self) -> None:
        """Deactivate the contact."""
        self.is_active = False
        self._touch()

    def activate(self) -> None:
        """Reactivate the contact."""
        self.is_active = True
        self._touch()

    def opt_out(self) -> None:
        """Opt out of messaging.

        Contact will not receive marketing messages.
        """
        self.opted_out = True
        self._touch()

    def opt_in(self) -> None:
        """Opt back into messaging."""
        self.opted_out = False
        self._touch()

    def rename(self, new_name: str) -> None:
        """Change contact name."""
        if not new_name or not new_name.strip():
            raise ValueError("Contact name must not be empty")
        self.name = new_name.strip()
        self._touch()

    def update_email(self, email: str | None) -> None:
        """Update contact email."""
        self.email = email.strip() if email else None
        self._touch()

    def can_receive_messages(self) -> bool:
        """Check if contact can receive messages."""
        return self.is_active and not self.opted_out

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Contact):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
