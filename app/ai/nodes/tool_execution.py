"""Tool execution node.

Calls approved use cases with validated parameters.
AI never writes to DB directly - only through use cases.
"""

from typing import Any

from app.ai.state import AIGraphState, ConfirmationStatus, Intent, ValidationResult
from app.config.logging import get_logger

logger = get_logger("ai.tool_execution")


async def execute_tool(state: AIGraphState) -> AIGraphState:
    """Execute the appropriate tool based on intent.

    Input: Confirmed intent + entities
    Output: Use case result

    Failure modes:
    - Use case exception → explain error
    - Provider error → explain error

    Stop condition: If tool fails

    CRITICAL: This node only executes if:
    1. Validation passed
    2. Confirmation received (for monetary actions)
    """
    # Safety checks - NEVER skip these
    if state.validation_result != ValidationResult.PASS:
        logger.warning(
            "tool_execution_blocked_validation",
            conversation_id=state.conversation_id,
        )
        return state

    if state.should_stop():
        return state

    if state.intent is None:
        return state

    # Check confirmation for monetary actions
    if Intent.requires_confirmation(state.intent):
        if state.confirmation_status != ConfirmationStatus.CONFIRMED:
            # Still waiting for confirmation
            return state

    logger.info(
        "tool_execution_start",
        conversation_id=state.conversation_id,
        intent=state.intent.value,
    )

    try:
        tool_name, result = await _dispatch_tool(state)

        logger.info(
            "tool_execution_success",
            conversation_id=state.conversation_id,
            tool=tool_name,
        )

        return state.with_updates(
            tool_name=tool_name,
            tool_result=result,
        )

    except Exception as e:
        logger.error(
            "tool_execution_error",
            conversation_id=state.conversation_id,
            error=str(e),
        )
        return state.with_updates(
            tool_error=str(e),
            response=f"Ocorreu um erro: {str(e)}",
        )


async def _dispatch_tool(state: AIGraphState) -> tuple[str, dict[str, Any]]:
    """Dispatch to the appropriate tool.

    TODO: Inject actual use cases via dependency injection.
    For now, returns placeholder results.
    """
    intent = state.intent

    if intent == Intent.CREATE_BOLETO:
        # TODO: Call CreateBoletoUseCase
        return "create_boleto", {
            "boleto_id": "placeholder_id",
            "status": "created",
            "amount_cents": state.entities.amount_cents,
            "due_date": state.entities.due_date,
        }

    if intent == Intent.CANCEL_BOLETO:
        # TODO: Call CancelBoletoUseCase
        return "cancel_boleto", {
            "boleto_id": state.entities.boleto_id,
            "status": "cancelled",
        }

    if intent == Intent.CHECK_STATUS:
        # TODO: Call GetBoletoStatusUseCase
        return "get_boleto_status", {
            "boleto_id": state.entities.boleto_id,
            "status": "pending",
        }

    if intent == Intent.SEND_MESSAGE:
        # TODO: Call QueueMessageUseCase
        return "queue_message", {
            "message_id": "placeholder_id",
            "status": "queued",
        }

    if intent == Intent.LIST_BOLETOS:
        # TODO: Call ListBoletosUseCase
        return "list_boletos", {
            "boletos": [],
            "count": 0,
        }

    return "none", {}
