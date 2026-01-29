"""Gemini LLM provider implementation.

Production-ready adapter for Google Gemini API.
Returns structured JSON only - no prose.
"""

import json

import httpx

from app.application.ports.providers.llm import (
    ExtractedEntitiesResult,
    IntentClassificationResult,
    LLMErrorCode,
    LLMProviderPort,
)
from app.config.logging import get_logger
from app.config.settings import get_settings

logger = get_logger("gemini_llm")

INTENT_CLASSIFICATION_PROMPT = """You are an intent classifier for a financial billing assistant.
Classify the user message into ONE of these intents:
- create_boleto: User wants to create a new boleto/billing
- cancel_boleto: User wants to cancel an existing boleto
- check_status: User wants to check the status of a boleto
- send_message: User wants to send a message/reminder
- list_boletos: User wants to list their boletos
- general_question: User has a general question
- unknown: Cannot determine intent

Return ONLY a JSON object with this exact structure:
{"intent": "<intent>", "confidence": <0.0-1.0>}

User message: {text}"""

ENTITY_EXTRACTION_PROMPT = """You are an entity extractor for a financial billing assistant.
Extract entities from the user message based on the intent: {intent}

For create_boleto, extract:
- contact_name: Name of the person to bill
- amount_cents: Amount in cents (e.g., "R$ 100,00" = 10000)
- due_date: Due date in YYYY-MM-DD format

For cancel_boleto or check_status, extract:
- boleto_id: The boleto identifier (UUID)

For send_message, extract:
- contact_name: Name of the recipient
- message_content: Message to send

Return ONLY a JSON object with extracted fields. Use null for missing fields.
Example: {{"contact_name": "João", "amount_cents": 10000, "due_date": "2026-02-15"}}

User message: {text}"""


class GeminiLLMProvider(LLMProviderPort):
    """Gemini LLM provider for intent classification and entity extraction.

    Features:
    - Structured JSON output only
    - Timeout handling
    - Error classification
    - No sensitive data logging
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.gemini_api_key
        self._model_name = model_name or settings.gemini_model_name
        self._timeout = timeout_seconds or settings.gemini_timeout_seconds
        self._base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def classify_intent(self, text: str) -> IntentClassificationResult:
        """Classify user intent using Gemini."""
        logger.info("gemini_classify_intent_start")

        prompt = INTENT_CLASSIFICATION_PROMPT.format(text=text)

        try:
            response = await self._call_gemini(prompt)

            if response is None:
                return IntentClassificationResult(
                    success=False,
                    error_code=LLMErrorCode.API_ERROR,
                    error_message="Empty response from Gemini",
                )

            try:
                data = json.loads(response)
                intent = data.get("intent", "unknown")
                confidence = float(data.get("confidence", 0.0))

                logger.info(
                    "gemini_classify_intent_success",
                    intent=intent,
                    confidence=confidence,
                )

                return IntentClassificationResult(
                    success=True,
                    intent=intent,
                    confidence=confidence,
                )

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning("gemini_parse_error", error=str(e))
                return IntentClassificationResult(
                    success=False,
                    error_code=LLMErrorCode.PARSE_ERROR,
                    error_message=f"Failed to parse response: {e}",
                )

        except httpx.TimeoutException:
            logger.error("gemini_timeout")
            return IntentClassificationResult(
                success=False,
                error_code=LLMErrorCode.TIMEOUT,
                error_message="Request timed out",
            )

        except Exception as e:
            logger.error("gemini_error", error=str(e))
            return IntentClassificationResult(
                success=False,
                error_code=LLMErrorCode.UNKNOWN,
                error_message=str(e),
            )

    async def extract_entities(
        self, text: str, intent: str
    ) -> ExtractedEntitiesResult:
        """Extract entities using Gemini."""
        logger.info("gemini_extract_entities_start", intent=intent)

        prompt = ENTITY_EXTRACTION_PROMPT.format(text=text, intent=intent)

        try:
            response = await self._call_gemini(prompt)

            if response is None:
                return ExtractedEntitiesResult(
                    success=False,
                    error_code=LLMErrorCode.API_ERROR,
                    error_message="Empty response from Gemini",
                )

            try:
                data = json.loads(response)

                amount_cents = data.get("amount_cents")
                if amount_cents is not None:
                    amount_cents = int(amount_cents)

                logger.info("gemini_extract_entities_success")

                return ExtractedEntitiesResult(
                    success=True,
                    contact_name=data.get("contact_name"),
                    contact_phone=data.get("contact_phone"),
                    amount_cents=amount_cents,
                    due_date=data.get("due_date"),
                    boleto_id=data.get("boleto_id"),
                    message_content=data.get("message_content"),
                )

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning("gemini_parse_error", error=str(e))
                return ExtractedEntitiesResult(
                    success=False,
                    error_code=LLMErrorCode.PARSE_ERROR,
                    error_message=f"Failed to parse response: {e}",
                )

        except httpx.TimeoutException:
            logger.error("gemini_timeout")
            return ExtractedEntitiesResult(
                success=False,
                error_code=LLMErrorCode.TIMEOUT,
                error_message="Request timed out",
            )

        except Exception as e:
            logger.error("gemini_error", error=str(e))
            return ExtractedEntitiesResult(
                success=False,
                error_code=LLMErrorCode.UNKNOWN,
                error_message=str(e),
            )

    async def _call_gemini(self, prompt: str) -> str | None:
        """Make API call to Gemini."""
        url = f"{self._base_url}/models/{self._model_name}:generateContent"

        headers = {"Content-Type": "application/json"}
        params = {"key": self._api_key}

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.95,
                "maxOutputTokens": 256,
            },
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                url,
                headers=headers,
                params=params,
                json=payload,
            )

            if response.status_code != 200:
                logger.error(
                    "gemini_api_error",
                    status_code=response.status_code,
                )
                return None

            data = response.json()
            candidates = data.get("candidates", [])

            if not candidates:
                return None

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])

            if not parts:
                return None

            text = parts[0].get("text", "")

            # Clean up markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            return text.strip()
