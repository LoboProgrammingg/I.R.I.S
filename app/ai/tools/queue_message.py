"""QueueMessage tool for AI.

Wraps QueueMessageUseCase for AI invocation.
Does NOT require confirmation (non-monetary).
"""

from dataclasses import dataclass
from typing import Any

from app.ai.tools.base import BaseTool, ToolResult
from app.application.messaging.dto import QueueMessageInput
from app.application.messaging.use_cases.queue_message import QueueMessageUseCase
from app.config.logging import get_logger

logger = get_logger("ai.tools.queue_message")


@dataclass
class QueueMessageToolInput:
    """Input for QueueMessage tool."""

    tenant_id: str
    contact_id: str
    message_type: str
    payload: dict[str, Any]
    idempotency_key: str


class QueueMessageTool(BaseTool[QueueMessageToolInput, dict]):
    """Tool for queueing messages.

    Preconditions:
    - Tenant must exist
    - Contact must exist in tenant
    - Contact must not have opted out

    Postconditions:
    - Message added to outbox
    - Will be delivered by Celery worker

    Idempotency:
    - Uses idempotency_key to prevent duplicates
    """

    def __init__(self, use_case: QueueMessageUseCase) -> None:
        self._use_case = use_case

    @property
    def name(self) -> str:
        return "queue_message"

    @property
    def requires_confirmation(self) -> bool:
        return False

    def validate_input(self, input_data: QueueMessageToolInput) -> list[str]:
        """Validate input before execution."""
        errors = []

        if not input_data.tenant_id:
            errors.append("tenant_id is required")

        if not input_data.contact_id:
            errors.append("contact_id is required")

        if not input_data.message_type:
            errors.append("message_type is required")

        if not input_data.idempotency_key:
            errors.append("idempotency_key is required")

        return errors

    async def execute(self, input_data: QueueMessageToolInput) -> ToolResult:
        """Execute QueueMessage use case."""
        errors = self.validate_input(input_data)
        if errors:
            return ToolResult(
                success=False,
                error="; ".join(errors),
            )

        logger.info(
            "queue_message_tool_start",
            tenant_id=input_data.tenant_id,
            message_type=input_data.message_type,
        )

        try:
            dto = QueueMessageInput(
                tenant_id=input_data.tenant_id,
                contact_id=input_data.contact_id,
                message_type=input_data.message_type,
                payload=input_data.payload,
                idempotency_key=input_data.idempotency_key,
            )

            outbox_item = await self._use_case.execute(dto)

            logger.info(
                "queue_message_tool_success",
                message_id=str(outbox_item.id.value),
            )

            return ToolResult(
                success=True,
                data={
                    "message_id": str(outbox_item.id.value),
                    "status": outbox_item.status.value,
                },
            )

        except Exception as e:
            logger.error(
                "queue_message_tool_error",
                error=str(e),
            )
            return ToolResult(
                success=False,
                error=str(e),
            )
