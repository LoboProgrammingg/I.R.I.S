"""Confirmation gate node.

Requests explicit user confirmation for monetary actions.
NEVER executes monetary actions without confirmation.
"""

from app.ai.state import AIGraphState, ConfirmationStatus, Intent, ValidationResult
from app.config.logging import get_logger

logger = get_logger("ai.confirmation_gate")


async def check_confirmation(state: AIGraphState) -> AIGraphState:
    """Check if confirmation is required and handle it.

    Input: Validated intent + entities
    Output: Confirmation status (pending/confirmed/rejected/not_required)

    Failure modes:
    - User rejects → cancel execution
    - Timeout → ask again

    Stop condition: If not confirmed for monetary action
    """
    if state.validation_result != ValidationResult.PASS:
        return state

    if state.should_stop():
        return state

    if state.intent is None:
        return state

    requires_confirmation = Intent.requires_confirmation(state.intent)

    if not requires_confirmation:
        logger.info(
            "confirmation_not_required",
            conversation_id=state.conversation_id,
            intent=state.intent.value,
        )
        return state.with_updates(
            confirmation_status=ConfirmationStatus.NOT_REQUIRED,
        )

    # Check if user already confirmed in this message
    normalized = (state.normalized_input or "").lower()
    confirmation_words = ["sim", "confirmo", "pode", "ok", "certo", "isso"]
    rejection_words = ["não", "nao", "cancela", "cancelar", "pare"]

    if any(word in normalized for word in rejection_words):
        logger.info(
            "confirmation_rejected",
            conversation_id=state.conversation_id,
        )
        return state.with_updates(
            confirmation_status=ConfirmationStatus.REJECTED,
            response="Operação cancelada.",
        )

    if any(word in normalized for word in confirmation_words):
        # Only confirm if we have a pending confirmation in context
        # For now, require explicit confirmation flow
        pass

    # Generate confirmation message
    confirmation_msg = _generate_confirmation_message(state)

    logger.info(
        "confirmation_pending",
        conversation_id=state.conversation_id,
        intent=state.intent.value,
    )

    return state.with_updates(
        confirmation_status=ConfirmationStatus.PENDING,
        confirmation_message=confirmation_msg,
        response=confirmation_msg,
    )


def _generate_confirmation_message(state: AIGraphState) -> str:
    """Generate confirmation message based on intent and entities."""
    if state.intent == Intent.CREATE_BOLETO:
        amount = state.entities.amount_cents or 0
        amount_formatted = f"R$ {amount / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        contact = state.entities.contact_name or "contato"
        due_date = state.entities.due_date or "data não especificada"

        # Format date for display
        if due_date and "-" in due_date:
            parts = due_date.split("-")
            if len(parts) == 3:
                due_date = f"{parts[2]}/{parts[1]}/{parts[0]}"

        return (
            f"Vou criar um boleto de **{amount_formatted}** "
            f"para **{contact}**, "
            f"com vencimento em **{due_date}**.\n\n"
            "Confirma? (Sim/Não)"
        )

    if state.intent == Intent.CANCEL_BOLETO:
        boleto_id = state.entities.boleto_id or "ID não especificado"
        return (
            f"Vou cancelar o boleto **{boleto_id}**.\n\n"
            "Confirma? (Sim/Não)"
        )

    return "Confirma a operação? (Sim/Não)"
