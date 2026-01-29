"""Identity & Tenancy bounded context - domain layer."""

from app.domain.identity.entities.tenant import Tenant
from app.domain.identity.entities.user import User
from app.domain.identity.exceptions import (
    IdentityDomainError,
    PhoneAlreadyRegisteredError,
    TenantInactiveError,
    TenantNotFoundError,
    UserInactiveError,
    UserNotFoundError,
)
from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.identity.value_objects.user_id import UserId
from app.domain.identity.value_objects.user_role import UserRole

__all__ = [
    "Tenant",
    "User",
    "TenantId",
    "UserId",
    "PhoneNumber",
    "UserRole",
    "IdentityDomainError",
    "TenantNotFoundError",
    "TenantInactiveError",
    "UserNotFoundError",
    "UserInactiveError",
    "PhoneAlreadyRegisteredError",
]
