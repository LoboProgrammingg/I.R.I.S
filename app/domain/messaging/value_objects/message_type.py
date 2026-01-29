"""MessageType value object."""

from enum import Enum


class MessageType(str, Enum):
    """Type of message to be sent.

    Determines message template and delivery priority.
    """

    BOLETO_SEND = "boleto_send"
    REMINDER = "reminder"
    NOTIFICATION = "notification"
