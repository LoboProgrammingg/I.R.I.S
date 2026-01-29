"""PhoneNumber value object."""

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    """E.164 normalized phone number.

    Format: +[country code][number]
    Example: +5511999998888

    Invariants:
    - Must start with +
    - Must contain only digits after +
    - Length between 8 and 15 digits (excluding +)
    """

    value: str

    _E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")

    def __post_init__(self) -> None:
        if not self._E164_PATTERN.match(self.value):
            raise ValueError(
                f"Invalid E.164 phone number: {self.value}. "
                "Must be in format +[country code][number], e.g., +5511999998888"
            )

    @classmethod
    def from_string(cls, value: str) -> "PhoneNumber":
        """Create PhoneNumber from string, normalizing if needed."""
        normalized = cls._normalize(value)
        return cls(value=normalized)

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize phone number to E.164 format."""
        digits = re.sub(r"[^\d+]", "", value)
        if not digits.startswith("+"):
            digits = "+" + digits
        return digits

    def masked(self) -> str:
        """Return masked version for logging: +55******1234."""
        if len(self.value) <= 6:
            return self.value
        return self.value[:3] + "******" + self.value[-4:]

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)
