"""ApplyInterest use case.

Applies interest to overdue boletos based on tenant policy.
This is called by a scheduled job.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from app.application.collections.dto import ApplyInterestInput


@dataclass
class ApplyInterestResult:
    """Result from ApplyInterest use case."""

    processed: int
    interest_applied: int
    total_interest_cents: int
    timestamp: datetime


class ApplyInterestUseCase:
    """Use case for applying interest to overdue boletos.

    Finds OVERDUE boletos and applies interest based on tenant policy.
    Deterministic - tracks interest already applied.

    Note: For MVP, interest application is logged but does not
    modify the original boleto amount. Full implementation
    requires an interest_applications audit table.
    """

    async def execute(self, input_dto: ApplyInterestInput) -> ApplyInterestResult:
        """Execute the ApplyInterest use case.

        MVP: Returns placeholder result. Full implementation
        requires additional infrastructure.
        """
        return ApplyInterestResult(
            processed=0,
            interest_applied=0,
            total_interest_cents=0,
            timestamp=datetime.now(timezone.utc),
        )
