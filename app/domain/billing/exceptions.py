"""Billing domain exceptions."""


class BillingDomainError(Exception):
    """Base exception for Billing domain errors."""

    pass


class BoletoNotFoundError(BillingDomainError):
    """Raised when a boleto is not found."""

    def __init__(self, boleto_id: str) -> None:
        self.boleto_id = boleto_id
        super().__init__(f"Boleto not found: {boleto_id}")


class BoletoAlreadyPaidError(BillingDomainError):
    """Raised when trying to modify a paid boleto."""

    def __init__(self, boleto_id: str) -> None:
        self.boleto_id = boleto_id
        super().__init__(f"Boleto already paid: {boleto_id}")


class BoletoAlreadyCancelledError(BillingDomainError):
    """Raised when trying to modify a cancelled boleto."""

    def __init__(self, boleto_id: str) -> None:
        self.boleto_id = boleto_id
        super().__init__(f"Boleto already cancelled: {boleto_id}")


class InvalidBoletoTransitionError(BillingDomainError):
    """Raised when an invalid status transition is attempted."""

    def __init__(self, boleto_id: str, from_status: str, to_status: str) -> None:
        self.boleto_id = boleto_id
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(
            f"Invalid transition for boleto {boleto_id}: {from_status} → {to_status}"
        )


class DuplicateBoletoError(BillingDomainError):
    """Raised when a boleto with same idempotency key exists."""

    def __init__(self, idempotency_key: str, tenant_id: str) -> None:
        self.idempotency_key = idempotency_key
        self.tenant_id = tenant_id
        super().__init__(
            f"Boleto with idempotency key {idempotency_key} already exists in tenant {tenant_id}"
        )


class PaymentNotFoundError(BillingDomainError):
    """Raised when a payment is not found."""

    def __init__(self, payment_id: str) -> None:
        self.payment_id = payment_id
        super().__init__(f"Payment not found: {payment_id}")


class BoletoProviderError(BillingDomainError):
    """Raised when a provider operation fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(f"Provider error: {message}")
