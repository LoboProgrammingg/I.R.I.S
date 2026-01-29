"""LLM Provider port for AI orchestration.

Defines the contract for LLM integration.
All implementations must return structured JSON - no prose.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class LLMErrorCode(str, Enum):
    """Error codes from LLM providers."""

    INVALID_INPUT = "invalid_input"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    API_ERROR = "api_error"
    PARSE_ERROR = "parse_error"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class IntentClassificationResult:
    """Result from intent classification.

    Returns structured data - no prose.
    """

    success: bool
    intent: str | None = None
    confidence: float = 0.0
    error_code: LLMErrorCode | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class ExtractedEntitiesResult:
    """Result from entity extraction.

    Returns structured data - no prose.
    """

    success: bool
    contact_name: str | None = None
    contact_phone: str | None = None
    amount_cents: int | None = None
    due_date: str | None = None
    boleto_id: str | None = None
    message_content: str | None = None
    error_code: LLMErrorCode | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone,
            "amount_cents": self.amount_cents,
            "due_date": self.due_date,
            "boleto_id": self.boleto_id,
            "message_content": self.message_content,
        }


class LLMProviderPort(ABC):
    """Port for LLM operations.

    All implementations must:
    - Return structured JSON only
    - Handle timeouts gracefully
    - Never return free-form prose
    - Be deterministic-friendly (same input → same output structure)
    """

    @abstractmethod
    async def classify_intent(self, text: str) -> IntentClassificationResult:
        """Classify user intent from text.

        Args:
            text: Normalized user input

        Returns:
            IntentClassificationResult with intent and confidence

        Must return one of:
        - create_boleto
        - cancel_boleto
        - check_status
        - send_message
        - list_boletos
        - general_question
        - unknown
        """
        ...

    @abstractmethod
    async def extract_entities(
        self, text: str, intent: str
    ) -> ExtractedEntitiesResult:
        """Extract structured entities from text.

        Args:
            text: Normalized user input
            intent: Classified intent (for context)

        Returns:
            ExtractedEntitiesResult with structured entities

        Entities extracted depend on intent:
        - create_boleto: contact_name, amount_cents, due_date
        - cancel_boleto: boleto_id
        - check_status: boleto_id
        - send_message: contact_name, message_content
        """
        ...
