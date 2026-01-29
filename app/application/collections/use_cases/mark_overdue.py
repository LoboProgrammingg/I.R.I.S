"""MarkOverdue use case.

Marks SENT boletos as OVERDUE when due date has passed.
This is called by a scheduled job.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from app.application.collections.dto import MarkOverdueInput
from app.application.ports.repositories.billing import BoletoRepositoryPort
from app.domain.billing.value_objects.boleto_status import BoletoStatus


@dataclass
class MarkOverdueResult:
    """Result from MarkOverdue use case."""

    processed: int
    marked_overdue: int
    timestamp: datetime


class MarkOverdueUseCase:
    """Use case for marking overdue boletos.

    Finds SENT boletos past due date and marks them as OVERDUE.
    Deterministic - safe to run multiple times.
    """

    def __init__(self, boleto_repository: BoletoRepositoryPort) -> None:
        self._boleto_repository = boleto_repository

    async def execute(self, input_dto: MarkOverdueInput) -> MarkOverdueResult:
        """Execute the MarkOverdue use case.

        Note: This requires a specialized repository method to query
        boletos by status and due_date. For MVP, we'll implement
        the logic in the Celery task directly with raw queries.
        """
        return MarkOverdueResult(
            processed=0,
            marked_overdue=0,
            timestamp=datetime.now(timezone.utc),
        )
