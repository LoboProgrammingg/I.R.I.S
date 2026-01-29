"""Stub messaging provider for development and testing.

This is a placeholder implementation that simulates message delivery.
Real WhatsApp integration will be added later.
"""

from typing import Any

from app.application.ports.providers.messaging import MessagingProviderPort, ProviderResult
from app.config.logging import get_logger


class StubMessagingProvider(MessagingProviderPort):
    """Stub implementation of MessagingProviderPort.

    Simulates successful message delivery for development.
    """

    def __init__(self) -> None:
        self._logger = get_logger("stub_messaging_provider")

    async def send(
        self,
        recipient_phone: str,
        message_type: str,
        payload: dict[str, Any],
    ) -> ProviderResult:
        """Simulate sending a message.

        Always returns success for stub implementation.
        """
        self._logger.info(
            "stub_message_sent",
            recipient_phone=recipient_phone,
            message_type=message_type,
            payload_keys=list(payload.keys()),
        )

        return ProviderResult(
            success=True,
            provider_message_id=f"stub_{message_type}_{recipient_phone}",
            error=None,
        )
