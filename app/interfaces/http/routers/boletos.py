"""HTTP router for Billing endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.application.billing.dto import (
    CancelBoletoInput,
    CreateBoletoInput,
    GetBoletoStatusInput,
)
from app.application.billing.use_cases.cancel_boleto import CancelBoletoUseCase
from app.application.billing.use_cases.create_boleto import CreateBoletoUseCase
from app.application.billing.use_cases.get_boleto_status import GetBoletoStatusUseCase
from app.domain.billing.entities.boleto import Boleto
from app.domain.billing.exceptions import (
    BoletoAlreadyCancelledError,
    BoletoAlreadyPaidError,
    BoletoNotFoundError,
    DuplicateBoletoError,
)
from app.domain.contacts.exceptions import ContactNotFoundError
from app.domain.identity.exceptions import TenantNotFoundError
from app.interfaces.http.dependencies.billing import (
    get_cancel_boleto_use_case,
    get_create_boleto_use_case,
    get_get_boleto_status_use_case,
)
from app.interfaces.http.schemas.billing import (
    BoletoResponse,
    CancelBoletoRequest,
    CreateBoletoRequest,
)

router = APIRouter(tags=["Billing"])


def _boleto_to_response(boleto: Boleto) -> BoletoResponse:
    """Map Boleto domain entity to response schema."""
    return BoletoResponse(
        id=str(boleto.id),
        tenant_id=str(boleto.tenant_id),
        contact_id=str(boleto.contact_id),
        amount_cents=boleto.amount.amount_cents,
        currency=boleto.amount.currency,
        due_date=str(boleto.due_date),
        status=boleto.status.value,
        idempotency_key=boleto.idempotency_key,
        provider_reference=boleto.provider_reference,
        created_at=boleto.created_at,
        updated_at=boleto.updated_at,
    )


@router.post(
    "/tenants/{tenant_id}/boletos",
    response_model=BoletoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new boleto",
)
async def create_boleto(
    tenant_id: Annotated[str, Path(description="Tenant UUID")],
    request: CreateBoletoRequest,
    use_case: Annotated[CreateBoletoUseCase, Depends(get_create_boleto_use_case)],
) -> BoletoResponse:
    """Create a new boleto for a contact within the tenant."""
    try:
        boleto = await use_case.execute(
            CreateBoletoInput(
                tenant_id=tenant_id,
                contact_id=request.contact_id,
                amount_cents=request.amount_cents,
                due_date=request.due_date,
                idempotency_key=request.idempotency_key,
                confirmed=request.confirmed,
            )
        )
        return _boleto_to_response(boleto)
    except TenantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "tenant_not_found", "message": str(e)},
        )
    except ContactNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "contact_not_found", "message": str(e)},
        )
    except DuplicateBoletoError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "duplicate_boleto", "message": str(e)},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": str(e)},
        )


@router.post(
    "/boletos/{boleto_id}/cancel",
    response_model=BoletoResponse,
    summary="Cancel a boleto",
)
async def cancel_boleto(
    boleto_id: Annotated[str, Path(description="Boleto UUID")],
    request: CancelBoletoRequest,
    use_case: Annotated[CancelBoletoUseCase, Depends(get_cancel_boleto_use_case)],
) -> BoletoResponse:
    """Cancel an existing boleto."""
    try:
        boleto = await use_case.execute(
            CancelBoletoInput(
                boleto_id=boleto_id,
                confirmed=request.confirmed,
            )
        )
        return _boleto_to_response(boleto)
    except BoletoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "boleto_not_found", "message": str(e)},
        )
    except BoletoAlreadyPaidError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "boleto_already_paid", "message": str(e)},
        )
    except BoletoAlreadyCancelledError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "boleto_already_cancelled", "message": str(e)},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": str(e)},
        )


@router.get(
    "/boletos/{boleto_id}",
    response_model=BoletoResponse,
    summary="Get boleto status",
)
async def get_boleto_status(
    boleto_id: Annotated[str, Path(description="Boleto UUID")],
    use_case: Annotated[GetBoletoStatusUseCase, Depends(get_get_boleto_status_use_case)],
) -> BoletoResponse:
    """Get the current status and details of a boleto."""
    try:
        boleto = await use_case.execute(
            GetBoletoStatusInput(boleto_id=boleto_id)
        )
        return _boleto_to_response(boleto)
    except BoletoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "boleto_not_found", "message": str(e)},
        )
