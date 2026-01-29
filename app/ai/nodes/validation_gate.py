"""Validation gate node.

Ensures all required entities are present and valid.
Blocks execution if validation fails.
"""

from app.ai.state import AIGraphState, Intent, ValidationResult
from app.config.logging import get_logger

logger = get_logger("ai.validation_gate")

# Required entities per intent
REQUIRED_ENTITIES: dict[Intent, list[str]] = {
    Intent.CREATE_BOLETO: ["contact_name", "amount_cents", "due_date"],
    Intent.CANCEL_BOLETO: ["boleto_id"],
    Intent.CHECK_STATUS: ["boleto_id"],
    Intent.SEND_MESSAGE: ["contact_name", "message_content"],
    Intent.LIST_BOLETOS: [],
    Intent.GENERAL_QUESTION: [],
    Intent.UNKNOWN: [],
}

# Human-readable field names for messages
FIELD_NAMES: dict[str, str] = {
    "contact_name": "nome do contato",
    "contact_phone": "telefone do contato",
    "amount_cents": "valor",
    "due_date": "data de vencimento",
    "boleto_id": "ID do boleto",
    "message_content": "conteúdo da mensagem",
}


async def validate_request(state: AIGraphState) -> AIGraphState:
    """Validate request completeness.

    Input: Intent + extracted entities
    Output: Validation result (pass/fail/clarify)

    Failure modes:
    - Missing required fields → ask for them
    - Invalid format → ask for correction

    Stop condition: If validation fails
    """
    if state.intent is None:
        return state

    if state.should_stop():
        return state

    logger.info(
        "validate_request_start",
        conversation_id=state.conversation_id,
        intent=state.intent.value,
    )

    required = REQUIRED_ENTITIES.get(state.intent, [])
    missing = []

    for field in required:
        value = getattr(state.entities, field, None)
        if value is None:
            missing.append(field)

    if missing:
        missing_names = [FIELD_NAMES.get(f, f) for f in missing]

        if len(missing_names) == 1:
            response = f"Para continuar, preciso saber: {missing_names[0]}."
        else:
            formatted = ", ".join(missing_names[:-1]) + f" e {missing_names[-1]}"
            response = f"Para continuar, preciso saber: {formatted}."

        logger.info(
            "validate_request_missing",
            conversation_id=state.conversation_id,
            missing=missing,
        )

        return state.with_updates(
            validation_result=ValidationResult.CLARIFY,
            validation_errors=missing,
            response=response,
        )

    # Additional validations
    errors = _validate_values(state)
    if errors:
        logger.info(
            "validate_request_invalid",
            conversation_id=state.conversation_id,
            errors=errors,
        )
        return state.with_updates(
            validation_result=ValidationResult.FAIL,
            validation_errors=errors,
            response=errors[0],
        )

    logger.info(
        "validate_request_pass",
        conversation_id=state.conversation_id,
    )

    return state.with_updates(
        validation_result=ValidationResult.PASS,
        validation_errors=[],
    )


def _validate_values(state: AIGraphState) -> list[str]:
    """Validate entity values."""
    errors = []

    if state.entities.amount_cents is not None:
        if state.entities.amount_cents <= 0:
            errors.append("O valor precisa ser positivo.")
        elif state.entities.amount_cents > 100_000_00:  # R$ 100k limit
            errors.append("O valor máximo permitido é R$ 100.000,00.")

    if state.entities.due_date is not None:
        from datetime import datetime

        try:
            due = datetime.strptime(state.entities.due_date, "%Y-%m-%d")
            if due.date() < datetime.now().date():
                errors.append("A data de vencimento não pode ser no passado.")
        except ValueError:
            errors.append("Data de vencimento inválida. Use o formato DD/MM/AAAA.")

    return errors
