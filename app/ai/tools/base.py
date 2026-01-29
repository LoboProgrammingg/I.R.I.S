"""Base tool interface for AI tools.

All AI tools must inherit from this base class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from app.config.logging import get_logger

logger = get_logger("ai.tools")

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


@dataclass
class ToolResult:
    """Result from tool execution."""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class BaseTool(ABC, Generic[TInput, TOutput]):
    """Base class for AI tools.

    Contract:
    - Tools call application layer only
    - Tools never access DB directly
    - Tools never call providers directly
    - Tools validate inputs independently
    - Tools are idempotent where applicable
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for logging and dispatch."""
        ...

    @property
    @abstractmethod
    def requires_confirmation(self) -> bool:
        """Whether this tool requires user confirmation."""
        ...

    @abstractmethod
    async def execute(self, input_data: TInput) -> ToolResult:
        """Execute the tool.

        Args:
            input_data: Validated input data

        Returns:
            ToolResult with success status and data or error
        """
        ...

    @abstractmethod
    def validate_input(self, input_data: TInput) -> list[str]:
        """Validate input data before execution.

        Returns:
            List of validation errors (empty if valid)
        """
        ...
