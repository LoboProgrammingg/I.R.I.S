"""Payment entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.billing.value_objects.boleto_id import BoletoId
from app.domain.billing.value_objects.money import Money
from app.domain.billing.value_objects.payment_id import PaymentId


@dataclass
class Payment:
    """Payment entity.

    Represents a confirmed payment for a boleto.
    One boleto = one payment (MVP).
    """

    id: PaymentId
    boleto_id: BoletoId
    amount: Money
    paid_at: datetime
    provider_reference: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate payment invariants."""
        if self.amount.amount_cents <= 0:
            raise ValueError("Payment amount must be positive")

    @classmethod
    def create(
        cls,
        boleto_id: BoletoId,
        amount: Money,
        paid_at: datetime | None = None,
        provider_reference: str | None = None,
        payment_id: PaymentId | None = None,
    ) -> "Payment":
        """Factory method to create a new Payment."""
        return cls(
            id=payment_id or PaymentId.generate(),
            boleto_id=boleto_id,
            amount=amount,
            paid_at=paid_at or datetime.now(timezone.utc),
            provider_reference=provider_reference,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Payment):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
