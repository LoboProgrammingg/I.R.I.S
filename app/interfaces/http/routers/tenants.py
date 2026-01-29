"""HTTP router for Identity & Tenancy endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.application.identity.dto import CreateTenantInput, CreateUserInput
from app.application.identity.use_cases.create_tenant import CreateTenantUseCase
from app.application.identity.use_cases.create_user import CreateUserUseCase
from app.domain.identity.entities.tenant import Tenant
from app.domain.identity.entities.user import User
from app.domain.identity.exceptions import (
    PhoneAlreadyRegisteredError,
    TenantNotFoundError,
)
from app.interfaces.http.dependencies.identity import (
    get_create_tenant_use_case,
    get_create_user_use_case,
)
from app.interfaces.http.schemas.identity import (
    CreateTenantRequest,
    CreateUserRequest,
    ErrorResponse,
    TenantResponse,
    UserResponse,
)

router = APIRouter(prefix="/tenants", tags=["Identity & Tenancy"])


def _tenant_to_response(tenant: Tenant) -> TenantResponse:
    """Map Tenant domain entity to response schema."""
    return TenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        is_active=tenant.is_active,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )


def _user_to_response(user: User) -> UserResponse:
    """Map User domain entity to response schema."""
    return UserResponse(
        id=str(user.id),
        tenant_id=str(user.tenant_id),
        phone_number=str(user.phone_number),
        name=user.name,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tenant",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
    },
)
async def create_tenant(
    request: CreateTenantRequest,
    use_case: Annotated[CreateTenantUseCase, Depends(get_create_tenant_use_case)],
) -> TenantResponse:
    """Create a new tenant in the system."""
    try:
        tenant = await use_case.execute(
            CreateTenantInput(name=request.name)
        )
        return _tenant_to_response(tenant)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": str(e)},
        )


@router.post(
    "/{tenant_id}/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user within a tenant",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        404: {"model": ErrorResponse, "description": "Tenant not found"},
        409: {"model": ErrorResponse, "description": "Phone already registered"},
    },
)
async def create_user(
    tenant_id: Annotated[str, Path(description="Tenant UUID")],
    request: CreateUserRequest,
    use_case: Annotated[CreateUserUseCase, Depends(get_create_user_use_case)],
) -> UserResponse:
    """Create a new user within the specified tenant."""
    try:
        user = await use_case.execute(
            CreateUserInput(
                tenant_id=tenant_id,
                phone_number=request.phone_number,
                name=request.name,
                role=request.role,
            )
        )
        return _user_to_response(user)
    except TenantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "tenant_not_found", "message": str(e)},
        )
    except PhoneAlreadyRegisteredError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "phone_already_registered", "message": str(e)},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": str(e)},
        )
