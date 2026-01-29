"""Money value object."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Money:
    """Value object representing monetary amount.

    Stores amount in cents to avoid floating point issues.
    Currency is BRL (Brazilian Real) for MVP.
    """

    amount_cents: int
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if self.amount_cents < 0:
            raise ValueError("Amount cannot be negative")
        if self.currency != "BRL":
            raise ValueError("Only BRL currency is supported")

    @classmethod
    def from_decimal(cls, amount: Decimal, currency: str = "BRL") -> "Money":
        """Create Money from decimal amount (e.g., 100.50)."""
        cents = int(amount * 100)
        return cls(amount_cents=cents, currency=currency)

    @classmethod
    def from_float(cls, amount: float, currency: str = "BRL") -> "Money":
        """Create Money from float amount (e.g., 100.50)."""
        cents = int(round(amount * 100))
        return cls(amount_cents=cents, currency=currency)

    def to_decimal(self) -> Decimal:
        """Convert to decimal representation."""
        return Decimal(self.amount_cents) / 100

    def to_float(self) -> float:
        """Convert to float representation."""
        return self.amount_cents / 100

    def __str__(self) -> str:
        return f"{self.currency} {self.to_decimal():.2f}"

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(
            amount_cents=self.amount_cents + other.amount_cents,
            currency=self.currency,
        )

    def __hash__(self) -> int:
        return hash((self.amount_cents, self.currency))
