"""DTOs for Billing use cases."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateBoletoInput:
    """Input for CreateBoleto use case."""

    tenant_id: str
    contact_id: str
    amount_cents: int
    due_date: str
    idempotency_key: str
    confirmed: bool = False


@dataclass(frozen=True)
class CancelBoletoInput:
    """Input for CancelBoleto use case."""

    boleto_id: str
    confirmed: bool = False
    reason: str | None = None


@dataclass(frozen=True)
class ProcessPaymentWebhookInput:
    """Input for ProcessPaymentWebhook use case."""

    provider_boleto_id: str
    amount_paid_cents: int
    paid_at: str
    idempotency_key: str


@dataclass(frozen=True)
class GetBoletoStatusInput:
    """Input for GetBoletoStatus use case."""

    boleto_id: str
