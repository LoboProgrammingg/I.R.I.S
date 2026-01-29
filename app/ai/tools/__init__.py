"""AI Tools - controlled wrappers for use cases.

Tools are the ONLY way the AI can interact with the system.
Each tool:
- Calls application layer use cases only
- Never accesses DB directly
- Never accesses providers directly
- Has explicit input/output contracts
- Is idempotent where possible
"""

from app.ai.tools.create_boleto import CreateBoletoTool
from app.ai.tools.cancel_boleto import CancelBoletoTool
from app.ai.tools.get_boleto_status import GetBoletoStatusTool
from app.ai.tools.queue_message import QueueMessageTool

__all__ = [
    "CreateBoletoTool",
    "CancelBoletoTool",
    "GetBoletoStatusTool",
    "QueueMessageTool",
]
