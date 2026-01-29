"""CreateBoleto tool for AI.

Wraps CreateBoletoUseCase for AI invocation.
Requires confirmation before execution.
"""

from dataclasses import dataclass

from app.ai.tools.base import BaseTool, ToolResult
from app.application.billing.dto import CreateBoletoInput
from app.application.billing.use_cases.create_boleto import CreateBoletoUseCase
from app.config.logging import get_logger

logger = get_logger("ai.tools.create_boleto")


@dataclass
class CreateBoletoToolInput:
    """Input for CreateBoleto tool."""

    tenant_id: str
    contact_id: str
    amount_cents: int
    due_date: str
    idempotency_key: str


class CreateBoletoTool(BaseTool[CreateBoletoToolInput, dict]):
    """Tool for creating boletos.

    Preconditions:
    - Tenant must exist
    - Contact must exist in tenant
    - Amount must be positive
    - Due date must be in future
    - User must have confirmed

    Postconditions:
    - Boleto created in Paytime
    - Boleto persisted with provider_reference
    - Status set to SENT

    Idempotency:
    - Uses idempotency_key to prevent duplicates
    """

    def __init__(self, use_case: CreateBoletoUseCase) -> None:
        self._use_case = use_case

    @property
    def name(self) -> str:
        return "create_boleto"

    @property
    def requires_confirmation(self) -> bool:
        return True

    def validate_input(self, input_data: CreateBoletoToolInput) -> list[str]:
        """Validate input before execution."""
        errors = []

        if not input_data.tenant_id:
            errors.append("tenant_id is required")

        if not input_data.contact_id:
            errors.append("contact_id is required")

        if input_data.amount_cents <= 0:
            errors.append("amount must be positive")

        if not input_data.due_date:
            errors.append("due_date is required")

        if not input_data.idempotency_key:
            errors.append("idempotency_key is required")

        return errors

    async def execute(self, input_data: CreateBoletoToolInput) -> ToolResult:
        """Execute CreateBoleto use case."""
        errors = self.validate_input(input_data)
        if errors:
            return ToolResult(
                success=False,
                error="; ".join(errors),
            )

        logger.info(
            "create_boleto_tool_start",
            tenant_id=input_data.tenant_id,
            amount_cents=input_data.amount_cents,
        )

        try:
            dto = CreateBoletoInput(
                tenant_id=input_data.tenant_id,
                contact_id=input_data.contact_id,
                amount_cents=input_data.amount_cents,
                due_date=input_data.due_date,
                idempotency_key=input_data.idempotency_key,
                confirmed=True,
            )

            boleto = await self._use_case.execute(dto)

            logger.info(
                "create_boleto_tool_success",
                boleto_id=str(boleto.id.value),
            )

            return ToolResult(
                success=True,
                data={
                    "boleto_id": str(boleto.id.value),
                    "status": boleto.status.value,
                    "amount_cents": boleto.amount.amount_cents,
                    "due_date": boleto.due_date.to_iso_string(),
                    "provider_reference": boleto.provider_reference,
                },
            )

        except Exception as e:
            logger.error(
                "create_boleto_tool_error",
                error=str(e),
            )
            return ToolResult(
                success=False,
                error=str(e),
            )
