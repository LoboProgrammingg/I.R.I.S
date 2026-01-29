"""AI Graph state model.

Defines the state that flows through the AI graph.
State is ephemeral (Redis) - only audit logs are persisted.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class Intent(str, Enum):
    """Allowed user intents.

    The AI can only classify into these categories.
    UNKNOWN triggers clarification flow.
    """

    CREATE_BOLETO = "create_boleto"
    CANCEL_BOLETO = "cancel_boleto"
    CHECK_STATUS = "check_status"
    SEND_MESSAGE = "send_message"
    LIST_BOLETOS = "list_boletos"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"

    @classmethod
    def requires_confirmation(cls, intent: "Intent") -> bool:
        """Check if intent requires explicit user confirmation."""
        return intent in {cls.CREATE_BOLETO, cls.CANCEL_BOLETO}


class ValidationResult(str, Enum):
    """Validation gate results."""

    PASS = "pass"
    FAIL = "fail"
    CLARIFY = "clarify"


class ConfirmationStatus(str, Enum):
    """Confirmation gate status."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    NOT_REQUIRED = "not_required"


@dataclass
class ExtractedEntities:
    """Entities extracted from user input.

    All fields are optional - validation gate checks required ones.
    """

    contact_name: str | None = None
    contact_phone: str | None = None
    amount_cents: int | None = None
    due_date: str | None = None
    boleto_id: str | None = None
    message_content: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone,
            "amount_cents": self.amount_cents,
            "due_date": self.due_date,
            "boleto_id": self.boleto_id,
            "message_content": self.message_content,
            "raw": self.raw,
        }


@dataclass
class AIGraphState:
    """State that flows through the AI graph.

    Immutable pattern: each node returns a new state.
    """

    # Identifiers
    conversation_id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str | None = None
    user_id: str | None = None

    # Input
    user_input: str = ""
    input_type: str = "text"  # text | audio
    normalized_input: str | None = None

    # Intent classification
    intent: Intent | None = None
    intent_confidence: float = 0.0

    # Entity extraction
    entities: ExtractedEntities = field(default_factory=ExtractedEntities)

    # Validation
    validation_result: ValidationResult = ValidationResult.FAIL
    validation_errors: list[str] = field(default_factory=list)

    # Confirmation
    confirmation_status: ConfirmationStatus = ConfirmationStatus.NOT_REQUIRED
    confirmation_message: str | None = None

    # Execution
    tool_name: str | None = None
    tool_result: dict[str, Any] | None = None
    tool_error: str | None = None

    # Response
    response: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    step_count: int = 0
    correlation_id: str | None = None

    def with_updates(self, **kwargs: Any) -> "AIGraphState":
        """Create a new state with updates.

        Immutable pattern - returns new instance.
        """
        current = {
            "conversation_id": self.conversation_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "user_input": self.user_input,
            "input_type": self.input_type,
            "normalized_input": self.normalized_input,
            "intent": self.intent,
            "intent_confidence": self.intent_confidence,
            "entities": self.entities,
            "validation_result": self.validation_result,
            "validation_errors": self.validation_errors,
            "confirmation_status": self.confirmation_status,
            "confirmation_message": self.confirmation_message,
            "tool_name": self.tool_name,
            "tool_result": self.tool_result,
            "tool_error": self.tool_error,
            "response": self.response,
            "created_at": self.created_at,
            "step_count": self.step_count + 1,
            "correlation_id": self.correlation_id,
        }
        current.update(kwargs)
        return AIGraphState(**current)

    def should_stop(self) -> bool:
        """Check if graph should stop execution."""
        if self.response is not None:
            return True
        if self.tool_error is not None:
            return True
        if self.confirmation_status == ConfirmationStatus.REJECTED:
            return True
        return False
