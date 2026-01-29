"""CancelBoleto tool for AI.

Wraps CancelBoletoUseCase for AI invocation.
Requires confirmation before execution.
"""

from dataclasses import dataclass

from app.ai.tools.base import BaseTool, ToolResult
from app.application.billing.dto import CancelBoletoInput
from app.application.billing.use_cases.cancel_boleto import CancelBoletoUseCase
from app.config.logging import get_logger

logger = get_logger("ai.tools.cancel_boleto")


@dataclass
class CancelBoletoToolInput:
    """Input for CancelBoleto tool."""

    boleto_id: str
    reason: str | None = None


class CancelBoletoTool(BaseTool[CancelBoletoToolInput, dict]):
    """Tool for cancelling boletos.

    Preconditions:
    - Boleto must exist
    - Boleto must not be already paid
    - Boleto must not be already cancelled
    - User must have confirmed

    Postconditions:
    - Boleto cancelled in Paytime
    - Boleto status set to CANCELLED
    - Pending reminders cancelled

    Idempotency:
    - Cancelling already cancelled boleto returns error
    """

    def __init__(self, use_case: CancelBoletoUseCase) -> None:
        self._use_case = use_case

    @property
    def name(self) -> str:
        return "cancel_boleto"

    @property
    def requires_confirmation(self) -> bool:
        return True

    def validate_input(self, input_data: CancelBoletoToolInput) -> list[str]:
        """Validate input before execution."""
        errors = []

        if not input_data.boleto_id:
            errors.append("boleto_id is required")

        return errors

    async def execute(self, input_data: CancelBoletoToolInput) -> ToolResult:
        """Execute CancelBoleto use case."""
        errors = self.validate_input(input_data)
        if errors:
            return ToolResult(
                success=False,
                error="; ".join(errors),
            )

        logger.info(
            "cancel_boleto_tool_start",
            boleto_id=input_data.boleto_id,
        )

        try:
            dto = CancelBoletoInput(
                boleto_id=input_data.boleto_id,
                confirmed=True,
                reason=input_data.reason,
            )

            boleto = await self._use_case.execute(dto)

            logger.info(
                "cancel_boleto_tool_success",
                boleto_id=str(boleto.id.value),
            )

            return ToolResult(
                success=True,
                data={
                    "boleto_id": str(boleto.id.value),
                    "status": boleto.status.value,
                },
            )

        except Exception as e:
            logger.error(
                "cancel_boleto_tool_error",
                error=str(e),
            )
            return ToolResult(
                success=False,
                error=str(e),
            )
