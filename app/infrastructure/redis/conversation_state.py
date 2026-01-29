"""Redis-based conversation state persistence.

Stores AI conversation state with TTL for ephemeral data.
No PII in logs.
"""

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

import redis.asyncio as redis

from app.ai.state import (
    AIGraphState,
    ConfirmationStatus,
    ExtractedEntities,
    Intent,
    ValidationResult,
)
from app.config.logging import get_logger
from app.config.settings import get_settings

logger = get_logger("redis.conversation_state")


class ConversationStateStore:
    """Redis-based conversation state storage.

    Features:
    - TTL-based expiration
    - Separate TTL for pending confirmations
    - JSON serialization
    - No PII logging
    """

    STATE_PREFIX = "ai:state:"
    CONFIRMATION_PREFIX = "ai:confirm:"

    def __init__(self, redis_url: str | None = None) -> None:
        settings = get_settings()
        self._redis_url = redis_url or settings.redis_url
        self._state_ttl = settings.ai_state_ttl_seconds
        self._confirmation_ttl = settings.ai_confirmation_ttl_seconds
        self._redis: redis.Redis | None = None

    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(self._redis_url, decode_responses=True)
        return self._redis

    async def save_state(
        self,
        conversation_id: str,
        state: AIGraphState,
        ttl_seconds: int | None = None,
    ) -> None:
        """Save conversation state to Redis.

        Args:
            conversation_id: Unique conversation identifier
            state: AI graph state to persist
            ttl_seconds: Optional TTL override (default: 30 minutes)
        """
        r = await self._get_redis()
        key = f"{self.STATE_PREFIX}{conversation_id}"
        ttl = ttl_seconds or self._state_ttl

        data = self._serialize_state(state)

        await r.setex(key, ttl, json.dumps(data))

        logger.info(
            "state_saved",
            conversation_id=conversation_id,
            ttl=ttl,
        )

    async def load_state(self, conversation_id: str) -> AIGraphState | None:
        """Load conversation state from Redis.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            AIGraphState if found, None if expired/missing
        """
        r = await self._get_redis()
        key = f"{self.STATE_PREFIX}{conversation_id}"

        data = await r.get(key)
        if data is None:
            logger.info(
                "state_not_found",
                conversation_id=conversation_id,
            )
            return None

        state = self._deserialize_state(json.loads(data))

        logger.info(
            "state_loaded",
            conversation_id=conversation_id,
        )

        return state

    async def delete_state(self, conversation_id: str) -> bool:
        """Delete conversation state from Redis.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            True if deleted, False if not found
        """
        r = await self._get_redis()
        key = f"{self.STATE_PREFIX}{conversation_id}"

        deleted = await r.delete(key)

        logger.info(
            "state_deleted",
            conversation_id=conversation_id,
            deleted=deleted > 0,
        )

        return deleted > 0

    async def save_pending_confirmation(
        self,
        conversation_id: str,
        confirmation_data: dict[str, Any],
    ) -> None:
        """Save pending confirmation with short TTL.

        Args:
            conversation_id: Unique conversation identifier
            confirmation_data: Data needed to complete confirmation
        """
        r = await self._get_redis()
        key = f"{self.CONFIRMATION_PREFIX}{conversation_id}"

        await r.setex(
            key,
            self._confirmation_ttl,
            json.dumps(confirmation_data),
        )

        logger.info(
            "confirmation_saved",
            conversation_id=conversation_id,
            ttl=self._confirmation_ttl,
        )

    async def load_pending_confirmation(
        self, conversation_id: str
    ) -> dict[str, Any] | None:
        """Load pending confirmation from Redis.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            Confirmation data if found, None if expired/missing
        """
        r = await self._get_redis()
        key = f"{self.CONFIRMATION_PREFIX}{conversation_id}"

        data = await r.get(key)
        if data is None:
            return None

        return json.loads(data)

    async def delete_pending_confirmation(self, conversation_id: str) -> bool:
        """Delete pending confirmation from Redis."""
        r = await self._get_redis()
        key = f"{self.CONFIRMATION_PREFIX}{conversation_id}"

        deleted = await r.delete(key)
        return deleted > 0

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None

    def _serialize_state(self, state: AIGraphState) -> dict[str, Any]:
        """Serialize state to JSON-compatible dict."""
        return {
            "conversation_id": state.conversation_id,
            "tenant_id": state.tenant_id,
            "user_id": state.user_id,
            "user_input": state.user_input,
            "input_type": state.input_type,
            "normalized_input": state.normalized_input,
            "intent": state.intent.value if state.intent else None,
            "intent_confidence": state.intent_confidence,
            "entities": state.entities.to_dict(),
            "validation_result": state.validation_result.value,
            "validation_errors": state.validation_errors,
            "confirmation_status": state.confirmation_status.value,
            "confirmation_message": state.confirmation_message,
            "tool_name": state.tool_name,
            "tool_result": state.tool_result,
            "tool_error": state.tool_error,
            "response": state.response,
            "created_at": state.created_at.isoformat(),
            "step_count": state.step_count,
        }

    def _deserialize_state(self, data: dict[str, Any]) -> AIGraphState:
        """Deserialize state from JSON dict."""
        intent = None
        if data.get("intent"):
            try:
                intent = Intent(data["intent"])
            except ValueError:
                intent = Intent.UNKNOWN

        entities_data = data.get("entities", {})
        entities = ExtractedEntities(
            contact_name=entities_data.get("contact_name"),
            contact_phone=entities_data.get("contact_phone"),
            amount_cents=entities_data.get("amount_cents"),
            due_date=entities_data.get("due_date"),
            boleto_id=entities_data.get("boleto_id"),
            message_content=entities_data.get("message_content"),
            raw=entities_data.get("raw", {}),
        )

        return AIGraphState(
            conversation_id=data["conversation_id"],
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
            user_input=data.get("user_input", ""),
            input_type=data.get("input_type", "text"),
            normalized_input=data.get("normalized_input"),
            intent=intent,
            intent_confidence=data.get("intent_confidence", 0.0),
            entities=entities,
            validation_result=ValidationResult(
                data.get("validation_result", "fail")
            ),
            validation_errors=data.get("validation_errors", []),
            confirmation_status=ConfirmationStatus(
                data.get("confirmation_status", "not_required")
            ),
            confirmation_message=data.get("confirmation_message"),
            tool_name=data.get("tool_name"),
            tool_result=data.get("tool_result"),
            tool_error=data.get("tool_error"),
            response=data.get("response"),
            created_at=datetime.fromisoformat(data["created_at"]),
            step_count=data.get("step_count", 0),
        )


# Singleton instance
_store: ConversationStateStore | None = None


def get_conversation_store() -> ConversationStateStore:
    """Get singleton conversation state store."""
    global _store
    if _store is None:
        _store = ConversationStateStore()
    return _store
