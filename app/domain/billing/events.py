"""Billing domain events.

These are definitions only - event publishing infrastructure comes later.
"""

from dataclasses import dataclass
from datetime import datetime

from app.domain.billing.value_objects.boleto_id import BoletoId
from app.domain.billing.value_objects.money import Money
from app.domain.billing.value_objects.payment_id import PaymentId


@dataclass(frozen=True)
class BoletoCreated:
    """Event raised when a new boleto is created."""

    boleto_id: BoletoId
    tenant_id: str
    contact_id: str
    amount: Money
    due_date: str
    occurred_at: datetime


@dataclass(frozen=True)
class BoletoSent:
    """Event raised when a boleto is sent to the contact."""

    boleto_id: BoletoId
    occurred_at: datetime


@dataclass(frozen=True)
class BoletoPaid:
    """Event raised when a boleto is paid."""

    boleto_id: BoletoId
    payment_id: PaymentId
    amount: Money
    occurred_at: datetime


@dataclass(frozen=True)
class BoletoOverdueMarked:
    """Event raised when a boleto is marked as overdue by scheduled job.
    
    Note: This is applied by a background job in the Collections context,
    not by real-time due date checking.
    """

    boleto_id: BoletoId
    due_date: str
    occurred_at: datetime


@dataclass(frozen=True)
class BoletoCancelled:
    """Event raised when a boleto is cancelled."""

    boleto_id: BoletoId
    reason: str | None
    occurred_at: datetime
