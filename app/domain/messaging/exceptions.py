"""Messaging domain exceptions."""


class MessagingDomainError(Exception):
    """Base exception for Messaging domain errors."""

    pass


class MessageNotFoundError(MessagingDomainError):
    """Raised when a message outbox item is not found."""

    def __init__(self, item_id: str) -> None:
        self.item_id = item_id
        super().__init__(f"Message outbox item not found: {item_id}")


class DuplicateMessageError(MessagingDomainError):
    """Raised when a message with same idempotency key exists."""

    def __init__(self, idempotency_key: str, tenant_id: str) -> None:
        self.idempotency_key = idempotency_key
        self.tenant_id = tenant_id
        super().__init__(
            f"Message with idempotency key {idempotency_key} already exists in tenant {tenant_id}"
        )


class ContactOptedOutError(MessagingDomainError):
    """Raised when trying to send message to opted-out contact."""

    def __init__(self, contact_id: str) -> None:
        self.contact_id = contact_id
        super().__init__(f"Contact has opted out of messages: {contact_id}")
