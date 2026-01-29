"""Input normalization node.

Normalizes user input to standard text format.
Handles text and audio inputs.
"""

from app.ai.state import AIGraphState
from app.config.logging import get_logger

logger = get_logger("ai.input_normalization")


async def normalize_input(state: AIGraphState) -> AIGraphState:
    """Normalize user input.

    Input: Raw user message (text or audio reference)
    Output: Normalized text string

    Failure modes:
    - Empty input → ask clarification
    - Audio transcription failure → ask retry

    Stop condition: If input is empty or malformed
    """
    logger.info(
        "normalize_input_start",
        conversation_id=state.conversation_id,
        input_type=state.input_type,
    )

    user_input = state.user_input.strip() if state.user_input else ""

    if not user_input:
        return state.with_updates(
            normalized_input=None,
            response="Não entendi sua mensagem. Pode repetir?",
        )

    # TODO: Audio transcription handling (future)
    # if state.input_type == "audio":
    #     transcribed = await transcribe_audio(user_input)
    #     if transcribed is None:
    #         return state.with_updates(
    #             response="Não consegui transcrever o áudio. Pode enviar novamente?"
    #         )
    #     user_input = transcribed

    normalized = user_input.lower().strip()

    logger.info(
        "normalize_input_complete",
        conversation_id=state.conversation_id,
        length=len(normalized),
    )

    return state.with_updates(normalized_input=normalized)
