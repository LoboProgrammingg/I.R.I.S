"""Boleto aggregate root."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.billing.exceptions import (
    BoletoAlreadyCancelledError,
    BoletoAlreadyPaidError,
    InvalidBoletoTransitionError,
)
from app.domain.billing.value_objects.boleto_id import BoletoId
from app.domain.billing.value_objects.boleto_status import BoletoStatus
from app.domain.billing.value_objects.due_date import DueDate
from app.domain.billing.value_objects.money import Money
from app.domain.contacts.value_objects.contact_id import ContactId
from app.domain.identity.value_objects.tenant_id import TenantId


@dataclass
class Boleto:
    """Boleto aggregate root.

    Represents a payment request instrument.

    Invariants:
    - Boleto belongs to exactly one tenant
    - Boleto references exactly one contact
    - A PAID boleto is immutable
    - Status transitions must be valid
    - Amount must be positive
    """

    id: BoletoId
    tenant_id: TenantId
    contact_id: ContactId
    amount: Money
    due_date: DueDate
    status: BoletoStatus
    idempotency_key: str
    provider_reference: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate boleto invariants."""
        if self.amount.amount_cents <= 0:
            raise ValueError("Boleto amount must be positive")
        if not self.idempotency_key or not self.idempotency_key.strip():
            raise ValueError("Idempotency key must not be empty")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        contact_id: ContactId,
        amount: Money,
        due_date: DueDate,
        idempotency_key: str,
        boleto_id: BoletoId | None = None,
    ) -> "Boleto":
        """Factory method to create a new Boleto."""
        return cls(
            id=boleto_id or BoletoId.generate(),
            tenant_id=tenant_id,
            contact_id=contact_id,
            amount=amount,
            due_date=due_date,
            status=BoletoStatus.CREATED,
            idempotency_key=idempotency_key.strip(),
        )

    def _check_not_terminal(self) -> None:
        """Ensure boleto is not in terminal state."""
        if self.status == BoletoStatus.PAID:
            raise BoletoAlreadyPaidError(str(self.id))
        if self.status == BoletoStatus.CANCELLED:
            raise BoletoAlreadyCancelledError(str(self.id))

    def _transition_to(self, new_status: BoletoStatus) -> None:
        """Safely transition to a new status."""
        if not self.status.can_transition_to(new_status):
            raise InvalidBoletoTransitionError(
                str(self.id), self.status.value, new_status.value
            )
        self.status = new_status
        self._touch()

    def mark_as_sent(self, provider_reference: str | None = None) -> None:
        """Mark boleto as sent."""
        self._check_not_terminal()
        self._transition_to(BoletoStatus.SENT)
        self.provider_reference = provider_reference

    def mark_as_paid(self) -> None:
        """Mark boleto as paid."""
        self._check_not_terminal()
        self._transition_to(BoletoStatus.PAID)

    def mark_as_overdue(self) -> None:
        """Mark boleto as overdue."""
        self._check_not_terminal()
        self._transition_to(BoletoStatus.OVERDUE)

    def cancel(self) -> None:
        """Cancel the boleto."""
        self._check_not_terminal()
        self._transition_to(BoletoStatus.CANCELLED)

    def is_paid(self) -> bool:
        """Check if boleto is paid."""
        return self.status == BoletoStatus.PAID

    def is_cancelled(self) -> bool:
        """Check if boleto is cancelled."""
        return self.status == BoletoStatus.CANCELLED

    def is_overdue(self) -> bool:
        """Check if boleto is overdue."""
        return self.status == BoletoStatus.OVERDUE or (
            self.status == BoletoStatus.SENT and self.due_date.is_past()
        )

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Boleto):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
