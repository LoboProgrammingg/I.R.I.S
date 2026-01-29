"""Add boletos and payments tables for Billing bounded context.

Revision ID: 004
Revises: 003
Create Date: 2026-01-29

Schema:
- boletos: Payment request instruments
- payments: Confirmed payments for boletos

Invariants enforced:
- Boleto belongs to one tenant (fk_boletos_tenant_id)
- Boleto references one contact (fk_boletos_contact_id)
- Idempotency key unique per tenant (uq_boletos_tenant_idempotency)
- One payment per boleto (unique constraint on boleto_id)
- ON DELETE RESTRICT on all FKs

Rollback: Safe, drops tables in correct order
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create boleto_status_enum type
    boleto_status_enum = postgresql.ENUM(
        "created", "sent", "paid", "overdue", "cancelled",
        name="boleto_status_enum",
    )
    boleto_status_enum.create(op.get_bind(), checkfirst=True)

    # Create boletos table
    op.create_table(
        "boletos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="BRL"),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "created", "sent", "paid", "overdue", "cancelled",
                name="boleto_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="created",
        ),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
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
            name="fk_boletos_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contacts.id"],
            name="fk_boletos_contact_id",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_boletos_tenant_idempotency"
        ),
    )

    op.create_index("ix_boletos_tenant_id", "boletos", ["tenant_id"])
    op.create_index("ix_boletos_contact_id", "boletos", ["contact_id"])

    # Create payments table
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("boleto_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="BRL"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("external_ref", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["boleto_id"],
            ["boletos.id"],
            name="fk_payments_boleto_id",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("boleto_id", name="uq_payments_boleto_id"),
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_index("ix_boletos_contact_id", table_name="boletos")
    op.drop_index("ix_boletos_tenant_id", table_name="boletos")
    op.drop_table("boletos")

    boleto_status_enum = postgresql.ENUM(
        "created", "sent", "paid", "overdue", "cancelled",
        name="boleto_status_enum",
    )
    boleto_status_enum.drop(op.get_bind(), checkfirst=True)
