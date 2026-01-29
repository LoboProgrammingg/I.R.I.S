"""AI Graph nodes.

Each node is a pure function that:
- Takes AIGraphState
- Returns AIGraphState (updated)
- Has no side effects except logging

Nodes are ordered and cannot be skipped.
"""

from app.ai.nodes.input_normalization import normalize_input
from app.ai.nodes.intent_classification import classify_intent
from app.ai.nodes.entity_extraction import extract_entities
from app.ai.nodes.validation_gate import validate_request
from app.ai.nodes.confirmation_gate import check_confirmation
from app.ai.nodes.tool_execution import execute_tool
from app.ai.nodes.response_generation import generate_response

__all__ = [
    "normalize_input",
    "classify_intent",
    "extract_entities",
    "validate_request",
    "check_confirmation",
    "execute_tool",
    "generate_response",
]
