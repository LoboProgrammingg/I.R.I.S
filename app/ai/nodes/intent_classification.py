"""Intent classification node.

Classifies user intent using LLM provider.
Returns confidence score for decision making.
"""

from app.ai.state import AIGraphState, Intent
from app.application.ports.providers.llm import LLMProviderPort
from app.config.logging import get_logger

logger = get_logger("ai.intent_classification")

# Confidence threshold for accepting classification
CONFIDENCE_THRESHOLD = 0.7

# Module-level provider (injected via set_llm_provider)
_llm_provider: LLMProviderPort | None = None


def set_llm_provider(provider: LLMProviderPort) -> None:
    """Set the LLM provider for intent classification."""
    global _llm_provider
    _llm_provider = provider


def get_llm_provider() -> LLMProviderPort:
    """Get the configured LLM provider."""
    if _llm_provider is None:
        from app.infrastructure.providers.llm_stub import StubLLMProvider
        return StubLLMProvider()
    return _llm_provider


async def classify_intent(state: AIGraphState) -> AIGraphState:
    """Classify user intent using LLM provider.

    Input: Normalized text
    Output: Intent enum + confidence score

    Failure modes:
    - Low confidence → ask clarification
    - Unknown intent → ask clarification
    - LLM error → fallback to unknown

    Stop condition: If confidence < 0.7
    """
    if state.normalized_input is None:
        return state

    if state.should_stop():
        return state

    logger.info(
        "classify_intent_start",
        conversation_id=state.conversation_id,
    )

    provider = get_llm_provider()
    result = await provider.classify_intent(state.normalized_input)

    if not result.success:
        logger.warning(
            "classify_intent_llm_error",
            conversation_id=state.conversation_id,
            error=result.error_message,
        )
        return state.with_updates(
            intent=Intent.UNKNOWN,
            intent_confidence=0.0,
            response="Desculpe, tive um problema ao entender sua mensagem. Pode repetir?",
        )

    intent = _map_intent(result.intent)
    confidence = result.confidence

    if confidence < CONFIDENCE_THRESHOLD:
        logger.info(
            "classify_intent_low_confidence",
            conversation_id=state.conversation_id,
            intent=intent.value,
            confidence=confidence,
        )
        return state.with_updates(
            intent=Intent.UNKNOWN,
            intent_confidence=confidence,
            response=(
                "Não tenho certeza do que você quer fazer. "
                "Você pode:\n"
                "- Criar um boleto\n"
                "- Cancelar um boleto\n"
                "- Ver status de um boleto\n"
                "- Enviar uma mensagem\n\n"
                "O que deseja?"
            ),
        )

    logger.info(
        "classify_intent_complete",
        conversation_id=state.conversation_id,
        intent=intent.value,
        confidence=confidence,
    )

    return state.with_updates(
        intent=intent,
        intent_confidence=confidence,
    )


def _map_intent(intent_str: str | None) -> Intent:
    """Map LLM intent string to Intent enum."""
    if intent_str is None:
        return Intent.UNKNOWN

    mapping = {
        "create_boleto": Intent.CREATE_BOLETO,
        "cancel_boleto": Intent.CANCEL_BOLETO,
        "check_status": Intent.CHECK_STATUS,
        "send_message": Intent.SEND_MESSAGE,
        "list_boletos": Intent.LIST_BOLETOS,
        "general_question": Intent.GENERAL_QUESTION,
    }

    return mapping.get(intent_str.lower(), Intent.UNKNOWN)
