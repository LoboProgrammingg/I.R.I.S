"""AI Graph definition.

Wires all nodes together in a deterministic flow.
Nodes execute in strict order - no skipping allowed.

Observability:
- correlation_id per request
- Structured logging for node transitions
- No PII in logs
"""

from uuid import uuid4

from app.ai.nodes import (
    classify_intent,
    check_confirmation,
    execute_tool,
    extract_entities,
    generate_response,
    normalize_input,
    validate_request,
)
from app.ai.state import AIGraphState
from app.config.logging import get_logger

logger = get_logger("ai.graph")


class AIGraph:
    """AI Orchestration Graph.

    Executes nodes in strict order:
    1. Input Normalization
    2. Intent Classification
    3. Entity Extraction
    4. Validation Gate
    5. Confirmation Gate
    6. Tool Execution
    7. Response Generation

    Each node can stop the flow by setting a response.

    Observability:
    - correlation_id injected at start
    - All logs include tenant_id, conversation_id
    - Node transitions logged
    - No PII logged
    """

    def __init__(self) -> None:
        self._nodes = [
            ("normalize_input", normalize_input),
            ("classify_intent", classify_intent),
            ("extract_entities", extract_entities),
            ("validate_request", validate_request),
            ("check_confirmation", check_confirmation),
            ("execute_tool", execute_tool),
            ("generate_response", generate_response),
        ]

    async def run(self, state: AIGraphState) -> AIGraphState:
        """Execute the graph.

        Args:
            state: Initial graph state

        Returns:
            Final state with response
        """
        # Inject correlation_id if not present
        if state.correlation_id is None:
            state = state.with_updates(correlation_id=str(uuid4())[:8])

        logger.info(
            "graph_run_start",
            correlation_id=state.correlation_id,
            conversation_id=state.conversation_id,
            tenant_id=state.tenant_id,
            input_length=len(state.user_input) if state.user_input else 0,
        )

        current_state = state

        for node_name, node_func in self._nodes:
            logger.info(
                "graph_node_enter",
                correlation_id=current_state.correlation_id,
                conversation_id=current_state.conversation_id,
                tenant_id=current_state.tenant_id,
                node=node_name,
                step=current_state.step_count,
            )

            current_state = await node_func(current_state)

            logger.info(
                "graph_node_exit",
                correlation_id=current_state.correlation_id,
                conversation_id=current_state.conversation_id,
                tenant_id=current_state.tenant_id,
                node=node_name,
                step=current_state.step_count,
                has_response=current_state.response is not None,
            )

            # Check if we should stop
            if current_state.should_stop():
                logger.info(
                    "graph_early_stop",
                    correlation_id=current_state.correlation_id,
                    conversation_id=current_state.conversation_id,
                    tenant_id=current_state.tenant_id,
                    node=node_name,
                    reason="response_set" if current_state.response else "error",
                )
                break

        logger.info(
            "graph_run_complete",
            correlation_id=current_state.correlation_id,
            conversation_id=current_state.conversation_id,
            tenant_id=current_state.tenant_id,
            steps=current_state.step_count,
            intent=current_state.intent.value if current_state.intent else None,
            has_response=current_state.response is not None,
        )

        return current_state


def create_graph() -> AIGraph:
    """Factory function to create the AI graph."""
    return AIGraph()
