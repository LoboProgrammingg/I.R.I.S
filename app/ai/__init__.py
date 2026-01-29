"""AI Orchestration layer for IRIS.

This module contains the AI graph that orchestrates:
- Intent classification
- Entity extraction
- Validation gates
- Confirmation handling
- Tool execution
- Response generation

The AI is a financial assistant that NEVER:
- Writes directly to database
- Decides monetary values
- Executes without confirmation
- Bypasses validation gates
"""

from app.ai.graph import create_graph
from app.ai.state import AIGraphState, Intent

__all__ = [
    "create_graph",
    "AIGraphState",
    "Intent",
]
