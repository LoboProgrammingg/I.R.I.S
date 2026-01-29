"""Messaging provider port for external message delivery."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ProviderResult:
    """Result from messaging provider."""

    success: bool
    provider_message_id: str | None = None
    error: str | None = None


class MessagingProviderPort(ABC):
    """Port for messaging provider (WhatsApp, SMS, etc.)."""

    @abstractmethod
    async def send(
        self,
        recipient_phone: str,
        message_type: str,
        payload: dict[str, Any],
    ) -> ProviderResult:
        """Send a message to a recipient.

        Args:
            recipient_phone: Phone number in E.164 format
            message_type: Type of message (boleto_send, reminder, etc.)
            payload: Message content

        Returns:
            ProviderResult with success status and optional error
        """
        ...
