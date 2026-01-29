"""HTTP router for Contacts endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.application.contacts.dto import (
    CreateContactInput,
    OptOutContactInput,
    UpdateContactInput,
)
from app.application.contacts.use_cases.create_contact import CreateContactUseCase
from app.application.contacts.use_cases.opt_out_contact import OptOutContactUseCase
from app.application.contacts.use_cases.update_contact import UpdateContactUseCase
from app.domain.contacts.entities.contact import Contact
from app.domain.contacts.exceptions import (
    ContactNotFoundError,
    ContactPhoneAlreadyExistsError,
)
from app.domain.identity.exceptions import TenantNotFoundError
from app.interfaces.http.dependencies.contacts import (
    get_create_contact_use_case,
    get_opt_out_contact_use_case,
    get_update_contact_use_case,
)
from app.interfaces.http.schemas.contacts import (
    ContactResponse,
    CreateContactRequest,
    OptOutRequest,
    UpdateContactRequest,
)

router = APIRouter(tags=["Contacts"])


def _contact_to_response(contact: Contact) -> ContactResponse:
    """Map Contact domain entity to response schema."""
    return ContactResponse(
        id=str(contact.id),
        tenant_id=str(contact.tenant_id),
        phone_number=str(contact.phone_number),
        name=contact.name,
        email=contact.email,
        is_active=contact.is_active,
        opted_out=contact.opted_out,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )


@router.post(
    "/tenants/{tenant_id}/contacts",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contact",
)
async def create_contact(
    tenant_id: Annotated[str, Path(description="Tenant UUID")],
    request: CreateContactRequest,
    use_case: Annotated[CreateContactUseCase, Depends(get_create_contact_use_case)],
) -> ContactResponse:
    """Create a new contact within the specified tenant."""
    try:
        contact = await use_case.execute(
            CreateContactInput(
                tenant_id=tenant_id,
                phone_number=request.phone_number,
                name=request.name,
                email=request.email,
            )
        )
        return _contact_to_response(contact)
    except TenantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "tenant_not_found", "message": str(e)},
        )
    except ContactPhoneAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "phone_already_exists", "message": str(e)},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": str(e)},
        )


@router.patch(
    "/contacts/{contact_id}",
    response_model=ContactResponse,
    summary="Update a contact",
)
async def update_contact(
    contact_id: Annotated[str, Path(description="Contact UUID")],
    request: UpdateContactRequest,
    use_case: Annotated[UpdateContactUseCase, Depends(get_update_contact_use_case)],
) -> ContactResponse:
    """Update an existing contact's information."""
    try:
        contact = await use_case.execute(
            UpdateContactInput(
                contact_id=contact_id,
                name=request.name,
                email=request.email,
            )
        )
        return _contact_to_response(contact)
    except ContactNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "contact_not_found", "message": str(e)},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": str(e)},
        )


@router.post(
    "/contacts/{contact_id}/opt-out",
    response_model=ContactResponse,
    summary="Manage contact opt-out preference",
)
async def opt_out_contact(
    contact_id: Annotated[str, Path(description="Contact UUID")],
    request: OptOutRequest,
    use_case: Annotated[OptOutContactUseCase, Depends(get_opt_out_contact_use_case)],
) -> ContactResponse:
    """Set or clear the contact's messaging opt-out preference."""
    try:
        contact = await use_case.execute(
            OptOutContactInput(
                contact_id=contact_id,
                opt_out=request.opt_out,
            )
        )
        return _contact_to_response(contact)
    except ContactNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "contact_not_found", "message": str(e)},
        )
