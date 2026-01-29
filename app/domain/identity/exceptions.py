"""Identity domain exceptions."""


class IdentityDomainError(Exception):
    """Base exception for Identity domain errors."""

    pass


class TenantNotFoundError(IdentityDomainError):
    """Raised when a tenant is not found."""

    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        super().__init__(f"Tenant not found: {tenant_id}")


class TenantInactiveError(IdentityDomainError):
    """Raised when trying to operate on an inactive tenant."""

    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        super().__init__(f"Tenant is inactive: {tenant_id}")


class UserNotFoundError(IdentityDomainError):
    """Raised when a user is not found."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")


class UserInactiveError(IdentityDomainError):
    """Raised when trying to operate with an inactive user."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User is inactive: {user_id}")


class PhoneAlreadyRegisteredError(IdentityDomainError):
    """Raised when phone number is already registered in tenant."""

    def __init__(self, phone_number: str, tenant_id: str) -> None:
        self.phone_number = phone_number
        self.tenant_id = tenant_id
        super().__init__(
            f"Phone number {phone_number} already registered in tenant {tenant_id}"
        )
