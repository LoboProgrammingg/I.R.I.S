"""HTTP router for Messaging Outbox endpoints (internal admin MVP)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.application.messaging.dto import QueueMessageInput
from app.application.messaging.use_cases.queue_message import QueueMessageUseCase
from app.domain.contacts.exceptions import ContactNotFoundError
from app.domain.identity.exceptions import TenantNotFoundError
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.messaging.entities.outbox_item import MessageOutboxItem
from app.domain.messaging.exceptions import ContactOptedOutError, DuplicateMessageError
from app.infrastructure.db.repositories.messaging import OutboxRepository
from app.interfaces.http.dependencies.messaging import (
    get_outbox_repository,
    get_queue_message_use_case,
)
from app.interfaces.http.schemas.messaging import (
    OutboxItemResponse,
    OutboxListResponse,
    QueueMessageRequest,
)

router = APIRouter(tags=["Messaging"])


def _item_to_response(item: MessageOutboxItem) -> OutboxItemResponse:
    """Map MessageOutboxItem to response schema."""
    return OutboxItemResponse(
        id=str(item.id),
        tenant_id=str(item.tenant_id),
        contact_id=str(item.contact_id),
        message_type=item.message_type.value,
        status=item.status.value,
        idempotency_key=item.idempotency_key,
        attempt_count=item.attempt_count,
        last_error=item.last_error,
        scheduled_at=item.scheduled_at,
        sent_at=item.sent_at,
        created_at=item.created_at,
    )


@router.post(
    "/tenants/{tenant_id}/outbox/queue",
    response_model=OutboxItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Queue a message for delivery",
)
async def queue_message(
    tenant_id: Annotated[str, Path(description="Tenant UUID")],
    request: QueueMessageRequest,
    use_case: Annotated[QueueMessageUseCase, Depends(get_queue_message_use_case)],
) -> OutboxItemResponse:
    """Queue a new message for delivery to a contact."""
    try:
        item = await use_case.execute(
            QueueMessageInput(
                tenant_id=tenant_id,
                contact_id=request.contact_id,
                message_type=request.message_type,
                payload=request.payload,
                idempotency_key=request.idempotency_key,
                scheduled_at=request.scheduled_at,
            )
        )
        return _item_to_response(item)
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
    except ContactOptedOutError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "contact_opted_out", "message": str(e)},
        )
    except DuplicateMessageError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "duplicate_message", "message": str(e)},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": str(e)},
        )


@router.get(
    "/tenants/{tenant_id}/outbox",
    response_model=OutboxListResponse,
    summary="List outbox items",
)
async def list_outbox(
    tenant_id: Annotated[str, Path(description="Tenant UUID")],
    status_filter: Annotated[
        str | None, Query(alias="status", description="Filter by status")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Max items")] = 50,
    repository: Annotated[OutboxRepository, Depends(get_outbox_repository)] = None,
) -> OutboxListResponse:
    """List outbox items for a tenant."""
    try:
        tid = TenantId.from_string(tenant_id)
        items = await repository.get_pending(tenant_id=tid, limit=limit)

        if status_filter:
            items = [i for i in items if i.status.value == status_filter]

        return OutboxListResponse(
            items=[_item_to_response(item) for item in items],
            count=len(items),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": str(e)},
        )
