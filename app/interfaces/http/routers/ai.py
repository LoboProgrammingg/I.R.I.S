"""AI HTTP endpoints.

Internal endpoints for AI orchestration.
Does NOT expose to public - internal use only.
"""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.graph import create_graph
from app.ai.state import AIGraphState, ConfirmationStatus
from app.config.logging import get_logger
from app.infrastructure.redis.conversation_state import (
    ConversationStateStore,
    get_conversation_store,
)
from app.interfaces.http.schemas.ai import (
    AIConfirmRequest,
    AIConfirmResponse,
    AIErrorResponse,
    AIMessageRequest,
    AIMessageResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])
logger = get_logger("ai.http")


def get_state_store() -> ConversationStateStore:
    """Dependency for conversation state store."""
    return get_conversation_store()


@router.post(
    "/message",
    response_model=AIMessageResponse,
    responses={
        400: {"model": AIErrorResponse, "description": "Invalid request"},
        500: {"model": AIErrorResponse, "description": "Internal error"},
    },
)
async def handle_message(
    request: AIMessageRequest,
    store: ConversationStateStore = Depends(get_state_store),
) -> AIMessageResponse:
    """Process a user message through the AI graph.

    - Creates new conversation or continues existing one
    - Runs full AI graph flow
    - Saves state to Redis
    - Returns response with confirmation status
    """
    correlation_id = str(uuid4())[:8]

    logger.info(
        "ai_message_start",
        correlation_id=correlation_id,
        tenant_id=request.tenant_id,
        conversation_id=request.conversation_id,
        text_length=len(request.text),
    )

    try:
        # Load existing state or create new
        if request.conversation_id:
            state = await store.load_state(request.conversation_id)
            if state is None:
                # Expired or not found - create new
                state = AIGraphState(
                    conversation_id=request.conversation_id,
                    tenant_id=request.tenant_id,
                    user_input=request.text,
                )
            else:
                # Update with new input
                state = state.with_updates(
                    user_input=request.text,
                    response=None,
                    tool_result=None,
                    tool_error=None,
                )
        else:
            conversation_id = str(uuid4())
            state = AIGraphState(
                conversation_id=conversation_id,
                tenant_id=request.tenant_id,
                user_input=request.text,
            )

        # Run AI graph
        graph = create_graph()
        final_state = await graph.run(state)

        # Check if confirmation is pending
        requires_confirmation = (
            final_state.confirmation_status == ConfirmationStatus.PENDING
        )

        # Save pending confirmation data if needed
        if requires_confirmation:
            await store.save_pending_confirmation(
                final_state.conversation_id,
                {
                    "intent": final_state.intent.value if final_state.intent else None,
                    "entities": final_state.entities.to_dict(),
                    "tenant_id": request.tenant_id,
                },
            )

        # Save state
        await store.save_state(final_state.conversation_id, final_state)

        logger.info(
            "ai_message_complete",
            correlation_id=correlation_id,
            conversation_id=final_state.conversation_id,
            intent=final_state.intent.value if final_state.intent else None,
            requires_confirmation=requires_confirmation,
        )

        return AIMessageResponse(
            conversation_id=final_state.conversation_id,
            response=final_state.response or "Não consegui processar sua mensagem.",
            requires_confirmation=requires_confirmation,
            suggested_action=(
                final_state.intent.value if final_state.intent else None
            ),
            intent=final_state.intent.value if final_state.intent else None,
        )

    except Exception as e:
        logger.error(
            "ai_message_error",
            correlation_id=correlation_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "code": "internal_error"},
        )


@router.post(
    "/confirm",
    response_model=AIConfirmResponse,
    responses={
        400: {"model": AIErrorResponse, "description": "Invalid request"},
        404: {"model": AIErrorResponse, "description": "Conversation not found"},
        410: {"model": AIErrorResponse, "description": "Confirmation expired"},
        500: {"model": AIErrorResponse, "description": "Internal error"},
    },
)
async def handle_confirm(
    request: AIConfirmRequest,
    store: ConversationStateStore = Depends(get_state_store),
) -> AIConfirmResponse:
    """Handle user confirmation for pending action.

    - Loads pending confirmation from Redis
    - Executes action if confirmed
    - Returns result
    """
    correlation_id = str(uuid4())[:8]

    logger.info(
        "ai_confirm_start",
        correlation_id=correlation_id,
        tenant_id=request.tenant_id,
        conversation_id=request.conversation_id,
        confirmed=request.confirmed,
    )

    try:
        # Load pending confirmation
        pending = await store.load_pending_confirmation(request.conversation_id)

        if pending is None:
            logger.warning(
                "ai_confirm_expired",
                correlation_id=correlation_id,
                conversation_id=request.conversation_id,
            )
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail={
                    "error": "Confirmação expirada. Por favor, tente novamente.",
                    "code": "confirmation_expired",
                    "conversation_id": request.conversation_id,
                },
            )

        # Load state
        state = await store.load_state(request.conversation_id)

        if state is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Conversa não encontrada.",
                    "code": "conversation_not_found",
                    "conversation_id": request.conversation_id,
                },
            )

        # Handle confirmation/rejection
        if not request.confirmed:
            # User rejected
            await store.delete_pending_confirmation(request.conversation_id)

            final_state = state.with_updates(
                confirmation_status=ConfirmationStatus.REJECTED,
                response="Operação cancelada.",
            )
            await store.save_state(request.conversation_id, final_state)

            logger.info(
                "ai_confirm_rejected",
                correlation_id=correlation_id,
                conversation_id=request.conversation_id,
            )

            return AIConfirmResponse(
                conversation_id=request.conversation_id,
                response="Operação cancelada.",
                action_executed=False,
            )

        # User confirmed - update state and run execution
        state = state.with_updates(
            confirmation_status=ConfirmationStatus.CONFIRMED,
            response=None,
        )

        # Run graph to execute tool
        graph = create_graph()
        final_state = await graph.run(state)

        # Cleanup confirmation
        await store.delete_pending_confirmation(request.conversation_id)
        await store.save_state(request.conversation_id, final_state)

        logger.info(
            "ai_confirm_executed",
            correlation_id=correlation_id,
            conversation_id=request.conversation_id,
            tool=final_state.tool_name,
            success=final_state.tool_error is None,
        )

        return AIConfirmResponse(
            conversation_id=request.conversation_id,
            response=final_state.response or "Operação concluída.",
            action_executed=final_state.tool_error is None,
            result=final_state.tool_result,
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "ai_confirm_error",
            correlation_id=correlation_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "code": "internal_error"},
        )
