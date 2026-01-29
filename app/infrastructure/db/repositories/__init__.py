"""Repository implementations."""

from app.infrastructure.db.repositories.billing import BoletoRepository, PaymentRepository
from app.infrastructure.db.repositories.collections import (
    InterestPolicyRepository,
    ReminderScheduleRepository,
)
from app.infrastructure.db.repositories.contacts import ContactRepository
from app.infrastructure.db.repositories.identity import TenantRepository, UserRepository
from app.infrastructure.db.repositories.messaging import OutboxRepository

__all__ = [
    "TenantRepository",
    "UserRepository",
    "ContactRepository",
    "BoletoRepository",
    "PaymentRepository",
    "OutboxRepository",
    "InterestPolicyRepository",
    "ReminderScheduleRepository",
]
