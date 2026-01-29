"""Add contacts table for Contacts bounded context.

Revision ID: 003
Revises: 002
Create Date: 2026-01-29

Schema:
- contacts: Person/entity that can receive boletos and messages

Invariants enforced:
- Contact belongs to exactly one tenant (fk_contacts_tenant_id)
- Phone number unique within tenant (uq_contacts_tenant_phone)
- ON DELETE RESTRICT prevents accidental tenant deletion

Rollback: Safe, drops contacts table
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("opted_out", sa.Boolean(), nullable=False, server_default="false"),
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
            name="fk_contacts_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "phone_number", name="uq_contacts_tenant_phone"),
    )

    op.create_index(
        "ix_contacts_tenant_id",
        "contacts",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_contacts_tenant_id", table_name="contacts")
    op.drop_table("contacts")
