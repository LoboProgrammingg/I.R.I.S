"""Contacts application layer - use cases and orchestration."""

from app.application.contacts.dto import (
    CreateContactInput,
    OptOutContactInput,
    UpdateContactInput,
)
from app.application.contacts.use_cases.create_contact import CreateContactUseCase
from app.application.contacts.use_cases.opt_out_contact import OptOutContactUseCase
from app.application.contacts.use_cases.update_contact import UpdateContactUseCase

__all__ = [
    "CreateContactInput",
    "UpdateContactInput",
    "OptOutContactInput",
    "CreateContactUseCase",
    "UpdateContactUseCase",
    "OptOutContactUseCase",
]
