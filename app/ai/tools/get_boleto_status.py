"""GetBoletoStatus tool for AI.

Wraps GetBoletoStatusUseCase for AI invocation.
Does NOT require confirmation (read-only).
"""

from dataclasses import dataclass

from app.ai.tools.base import BaseTool, ToolResult
from app.application.billing.dto import GetBoletoStatusInput
from app.application.billing.use_cases.get_boleto_status import GetBoletoStatusUseCase
from app.config.logging import get_logger

logger = get_logger("ai.tools.get_boleto_status")


@dataclass
class GetBoletoStatusToolInput:
    """Input for GetBoletoStatus tool."""

    boleto_id: str


class GetBoletoStatusTool(BaseTool[GetBoletoStatusToolInput, dict]):
    """Tool for checking boleto status.

    Preconditions:
    - Boleto must exist

    Postconditions:
    - Returns current boleto status
    - No state changes

    Idempotency:
    - Always safe to call (read-only)
    """

    def __init__(self, use_case: GetBoletoStatusUseCase) -> None:
        self._use_case = use_case

    @property
    def name(self) -> str:
        return "get_boleto_status"

    @property
    def requires_confirmation(self) -> bool:
        return False

    def validate_input(self, input_data: GetBoletoStatusToolInput) -> list[str]:
        """Validate input before execution."""
        errors = []

        if not input_data.boleto_id:
            errors.append("boleto_id is required")

        return errors

    async def execute(self, input_data: GetBoletoStatusToolInput) -> ToolResult:
        """Execute GetBoletoStatus use case."""
        errors = self.validate_input(input_data)
        if errors:
            return ToolResult(
                success=False,
                error="; ".join(errors),
            )

        logger.info(
            "get_boleto_status_tool_start",
            boleto_id=input_data.boleto_id,
        )

        try:
            dto = GetBoletoStatusInput(boleto_id=input_data.boleto_id)
            boleto = await self._use_case.execute(dto)

            logger.info(
                "get_boleto_status_tool_success",
                boleto_id=str(boleto.id.value),
                status=boleto.status.value,
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
                "get_boleto_status_tool_error",
                error=str(e),
            )
            return ToolResult(
                success=False,
                error=str(e),
            )
