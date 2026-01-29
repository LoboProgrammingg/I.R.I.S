"""DTOs for Contacts use cases.

Plain dataclasses for input/output. No framework dependencies.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateContactInput:
    """Input for CreateContact use case."""

    tenant_id: str
    phone_number: str
    name: str
    email: str | None = None


@dataclass(frozen=True)
class UpdateContactInput:
    """Input for UpdateContact use case."""

    contact_id: str
    name: str | None = None
    email: str | None = None


@dataclass(frozen=True)
class OptOutContactInput:
    """Input for OptOutContact use case."""

    contact_id: str
    opt_out: bool = True
