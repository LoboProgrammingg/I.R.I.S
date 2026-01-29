"""Stub LLM provider for testing.

Returns predictable responses based on keywords.
No actual LLM calls.
"""

import re
from datetime import datetime, timedelta

from app.application.ports.providers.llm import (
    ExtractedEntitiesResult,
    IntentClassificationResult,
    LLMProviderPort,
)
from app.config.logging import get_logger

logger = get_logger("llm_stub")


class StubLLMProvider(LLMProviderPort):
    """Stub LLM provider for testing and development."""

    async def classify_intent(self, text: str) -> IntentClassificationResult:
        """Classify intent using keywords."""
        logger.info("stub_classify_intent", text_length=len(text))

        text_lower = text.lower()

        create_keywords = ["criar", "gerar", "emitir", "novo boleto", "cobrar"]
        cancel_keywords = ["cancelar", "anular", "cancelamento"]
        status_keywords = ["status", "situação", "como está", "verificar", "checar"]
        send_keywords = ["enviar", "mandar", "mensagem", "lembrete"]
        list_keywords = ["listar", "mostrar", "quais boletos", "meus boletos"]

        if any(kw in text_lower for kw in create_keywords):
            return IntentClassificationResult(
                success=True, intent="create_boleto", confidence=0.85
            )

        if any(kw in text_lower for kw in cancel_keywords):
            return IntentClassificationResult(
                success=True, intent="cancel_boleto", confidence=0.85
            )

        if any(kw in text_lower for kw in status_keywords):
            return IntentClassificationResult(
                success=True, intent="check_status", confidence=0.85
            )

        if any(kw in text_lower for kw in send_keywords):
            return IntentClassificationResult(
                success=True, intent="send_message", confidence=0.80
            )

        if any(kw in text_lower for kw in list_keywords):
            return IntentClassificationResult(
                success=True, intent="list_boletos", confidence=0.80
            )

        return IntentClassificationResult(
            success=True, intent="unknown", confidence=0.3
        )

    async def extract_entities(
        self, text: str, intent: str
    ) -> ExtractedEntitiesResult:
        """Extract entities using regex patterns."""
        logger.info("stub_extract_entities", intent=intent)

        contact_name = None
        contact_phone = None
        amount_cents = None
        due_date = None
        boleto_id = None
        message_content = None

        # Extract amount
        amount_patterns = [
            r"r\$\s*([\d.,]+)",
            r"(\d+(?:[.,]\d+)?)\s*(?:reais|real)",
            r"valor\s*(?:de)?\s*r?\$?\s*([\d.,]+)",
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(".", "").replace(",", ".")
                try:
                    amount_cents = int(float(amount_str) * 100)
                except ValueError:
                    pass
                break

        # Extract date
        if "amanhã" in text.lower() or "amanha" in text.lower():
            tomorrow = datetime.now() + timedelta(days=1)
            due_date = tomorrow.strftime("%Y-%m-%d")
        elif "hoje" in text.lower():
            due_date = datetime.now().strftime("%Y-%m-%d")
        else:
            date_pattern = r"(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?"
            match = re.search(date_pattern, text)
            if match:
                try:
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = datetime.now().year
                    if match.lastindex >= 3 and match.group(3):
                        year = int(match.group(3))
                        if year < 100:
                            year += 2000
                    due_date = f"{year:04d}-{month:02d}-{day:02d}"
                except (ValueError, IndexError):
                    pass

        # Extract phone
        phone_pattern = r"(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[\s\-]?\d{4}"
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            phone = re.sub(r"[^\d]", "", phone_match.group())
            if len(phone) >= 10:
                contact_phone = phone

        # Extract name
        name_pattern = r"(?:para|de|cliente)\s+([A-Za-zÀ-ú]+(?:\s+[A-Za-zÀ-ú]+)?)"
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            contact_name = name_match.group(1).strip().title()

        # Extract boleto ID (UUID pattern)
        uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        uuid_match = re.search(uuid_pattern, text, re.IGNORECASE)
        if uuid_match:
            boleto_id = uuid_match.group()

        return ExtractedEntitiesResult(
            success=True,
            contact_name=contact_name,
            contact_phone=contact_phone,
            amount_cents=amount_cents,
            due_date=due_date,
            boleto_id=boleto_id,
            message_content=message_content,
        )
