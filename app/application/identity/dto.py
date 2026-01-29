"""DTOs for Identity & Tenancy use cases.

Plain dataclasses for input/output. No framework dependencies.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTenantInput:
    """Input for CreateTenant use case."""

    name: str


@dataclass(frozen=True)
class CreateUserInput:
    """Input for CreateUser use case."""

    tenant_id: str
    phone_number: str
    name: str
    role: str = "user"
