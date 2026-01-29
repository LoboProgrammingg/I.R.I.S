"""Response generation node.

Generates human-readable response based on tool result.
Responses are deterministic - no LLM creativity here.
"""

from app.ai.state import AIGraphState, Intent
from app.config.logging import get_logger

logger = get_logger("ai.response_generation")


async def generate_response(state: AIGraphState) -> AIGraphState:
    """Generate user-facing response.

    Input: Tool result or error
    Output: User-facing message

    Failure modes: None (deterministic formatting)

    This node always succeeds - it just formats existing data.
    """
    # If response already set (error or clarification), keep it
    if state.response is not None:
        return state

    if state.tool_error is not None:
        return state.with_updates(
            response=f"Não foi possível completar a operação: {state.tool_error}"
        )

    if state.tool_result is None:
        return state.with_updates(
            response="Operação concluída."
        )

    logger.info(
        "generate_response_start",
        conversation_id=state.conversation_id,
        tool=state.tool_name,
    )

    response = _format_response(state)

    logger.info(
        "generate_response_complete",
        conversation_id=state.conversation_id,
    )

    return state.with_updates(response=response)


def _format_response(state: AIGraphState) -> str:
    """Format response based on intent and result."""
    result = state.tool_result or {}
    intent = state.intent

    if intent == Intent.CREATE_BOLETO:
        amount = result.get("amount_cents", 0)
        amount_formatted = f"R$ {amount / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        boleto_id = result.get("boleto_id", "")
        due_date = result.get("due_date", "")

        if due_date and "-" in due_date:
            parts = due_date.split("-")
            if len(parts) == 3:
                due_date = f"{parts[2]}/{parts[1]}/{parts[0]}"

        return (
            f"✅ Boleto criado com sucesso!\n\n"
            f"**Valor:** {amount_formatted}\n"
            f"**Vencimento:** {due_date}\n"
            f"**ID:** {boleto_id}\n\n"
            "O boleto será enviado ao contato."
        )

    if intent == Intent.CANCEL_BOLETO:
        boleto_id = result.get("boleto_id", "")
        return f"✅ Boleto **{boleto_id}** cancelado com sucesso."

    if intent == Intent.CHECK_STATUS:
        boleto_id = result.get("boleto_id", "")
        status = result.get("status", "desconhecido")
        status_map = {
            "created": "Criado",
            "sent": "Enviado",
            "paid": "Pago",
            "overdue": "Vencido",
            "cancelled": "Cancelado",
        }
        status_display = status_map.get(status, status)
        return f"📋 Status do boleto **{boleto_id}**: {status_display}"

    if intent == Intent.SEND_MESSAGE:
        return "✅ Mensagem adicionada à fila de envio."

    if intent == Intent.LIST_BOLETOS:
        boletos = result.get("boletos", [])
        count = result.get("count", 0)
        if count == 0:
            return "📋 Você não tem boletos no momento."
        return f"📋 Você tem {count} boleto(s)."

    return "✅ Operação concluída."
