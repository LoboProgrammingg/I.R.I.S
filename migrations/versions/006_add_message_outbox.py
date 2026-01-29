"""Add message_outbox table for Messaging bounded context.

Revision ID: 006
Revises: 005
Create Date: 2026-01-29

Purpose:
- Outbox Pattern for reliable message delivery
- Track message status and retry attempts

Schema:
- message_outbox: Queued messages for delivery

Invariants enforced:
- Tenant isolation (fk_message_outbox_tenant_id)
- Contact reference (fk_message_outbox_contact_id)
- Idempotency key unique per tenant (uq_message_outbox_tenant_idempotency)

Rollback: Safe, drops table and enums
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    message_type_enum = postgresql.ENUM(
        "boleto_send", "reminder", "notification",
        name="message_type_enum",
    )
    message_type_enum.create(op.get_bind(), checkfirst=True)

    delivery_status_enum = postgresql.ENUM(
        "pending", "sent", "failed", "retrying",
        name="delivery_status_enum",
    )
    delivery_status_enum.create(op.get_bind(), checkfirst=True)

    # Create message_outbox table
    op.create_table(
        "message_outbox",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "message_type",
            postgresql.ENUM(
                "boleto_send", "reminder", "notification",
                name="message_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending", "sent", "failed", "retrying",
                name="delivery_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("payload", postgresql.JSON(), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "scheduled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_message_outbox_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contacts.id"],
            name="fk_message_outbox_contact_id",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_message_outbox_tenant_idempotency"
        ),
    )

    op.create_index("ix_message_outbox_tenant_id", "message_outbox", ["tenant_id"])
    op.create_index("ix_message_outbox_contact_id", "message_outbox", ["contact_id"])
    op.create_index("ix_message_outbox_status", "message_outbox", ["status"])


def downgrade() -> None:
    op.drop_index("ix_message_outbox_status", table_name="message_outbox")
    op.drop_index("ix_message_outbox_contact_id", table_name="message_outbox")
    op.drop_index("ix_message_outbox_tenant_id", table_name="message_outbox")
    op.drop_table("message_outbox")

    delivery_status_enum = postgresql.ENUM(
        "pending", "sent", "failed", "retrying",
        name="delivery_status_enum",
    )
    delivery_status_enum.drop(op.get_bind(), checkfirst=True)

    message_type_enum = postgresql.ENUM(
        "boleto_send", "reminder", "notification",
        name="message_type_enum",
    )
    message_type_enum.drop(op.get_bind(), checkfirst=True)
