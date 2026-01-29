"""Contacts domain exceptions."""


class ContactDomainError(Exception):
    """Base exception for Contacts domain errors."""

    pass


class ContactNotFoundError(ContactDomainError):
    """Raised when a contact is not found."""

    def __init__(self, contact_id: str) -> None:
        self.contact_id = contact_id
        super().__init__(f"Contact not found: {contact_id}")


class ContactPhoneAlreadyExistsError(ContactDomainError):
    """Raised when phone number already exists in tenant."""

    def __init__(self, phone_number: str, tenant_id: str) -> None:
        self.phone_number = phone_number
        self.tenant_id = tenant_id
        super().__init__(
            f"Contact with phone {phone_number} already exists in tenant {tenant_id}"
        )
