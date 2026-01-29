"""Entity extraction node.

Extracts structured entities from user input using LLM provider.
Validation gate checks completeness - this node just extracts.
"""

from app.ai.state import AIGraphState, ExtractedEntities
from app.application.ports.providers.llm import LLMProviderPort
from app.config.logging import get_logger

logger = get_logger("ai.entity_extraction")

# Module-level provider (injected via set_llm_provider)
_llm_provider: LLMProviderPort | None = None


def set_llm_provider(provider: LLMProviderPort) -> None:
    """Set the LLM provider for entity extraction."""
    global _llm_provider
    _llm_provider = provider


def get_llm_provider() -> LLMProviderPort:
    """Get the configured LLM provider."""
    if _llm_provider is None:
        from app.infrastructure.providers.llm_stub import StubLLMProvider
        return StubLLMProvider()
    return _llm_provider


async def extract_entities(state: AIGraphState) -> AIGraphState:
    """Extract entities from user input using LLM provider.

    Input: Normalized text + intent
    Output: Extracted entities (contact, amount, date, etc.)

    Failure modes:
    - LLM error → continue with empty entities
    - Missing entities → validation gate handles

    This node extracts what it can; validation gate enforces requirements.
    """
    if state.intent is None:
        return state

    if state.should_stop():
        return state

    logger.info(
        "extract_entities_start",
        conversation_id=state.conversation_id,
        intent=state.intent.value,
    )

    provider = get_llm_provider()
    result = await provider.extract_entities(
        state.normalized_input or "",
        state.intent.value,
    )

    if not result.success:
        logger.warning(
            "extract_entities_llm_error",
            conversation_id=state.conversation_id,
            error=result.error_message,
        )
        # Continue with empty entities - validation gate will catch missing
        return state.with_updates(entities=ExtractedEntities())

    entities = ExtractedEntities(
        contact_name=result.contact_name,
        contact_phone=result.contact_phone,
        amount_cents=result.amount_cents,
        due_date=result.due_date,
        boleto_id=result.boleto_id,
        message_content=result.message_content,
        raw={"llm_extracted": True},
    )

    logger.info(
        "extract_entities_complete",
        conversation_id=state.conversation_id,
        has_contact=entities.contact_name is not None,
        has_amount=entities.amount_cents is not None,
        has_date=entities.due_date is not None,
    )

    return state.with_updates(entities=entities)
