"""Add interest_policies and reminder_schedules tables for Collections.

Revision ID: 007
Revises: 006
Create Date: 2026-01-29

Purpose:
- Store interest/penalty configuration per tenant
- Schedule reminders for overdue boletos

Schema:
- interest_policies: Tenant-specific interest configuration
- reminder_schedules: Scheduled reminders for boletos

Invariants enforced:
- One active policy per tenant (partial unique constraint)
- FK RESTRICT on tenant and boleto references

Rollback: Safe, drops tables and enums
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create reminder_status_enum
    reminder_status_enum = postgresql.ENUM(
        "pending", "sent", "cancelled",
        name="reminder_status_enum",
    )
    reminder_status_enum.create(op.get_bind(), checkfirst=True)

    # Create interest_policies table
    op.create_table(
        "interest_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("grace_period_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("daily_interest_rate_bps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fixed_penalty_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
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
            name="fk_interest_policies_tenant_id",
            ondelete="RESTRICT",
        ),
    )

    op.create_index("ix_interest_policies_tenant_id", "interest_policies", ["tenant_id"])

    # Create reminder_schedules table
    op.create_table(
        "reminder_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("boleto_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending", "sent", "cancelled",
                name="reminder_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_reminder_schedules_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["boleto_id"],
            ["boletos.id"],
            name="fk_reminder_schedules_boleto_id",
            ondelete="RESTRICT",
        ),
    )

    op.create_index("ix_reminder_schedules_tenant_id", "reminder_schedules", ["tenant_id"])
    op.create_index("ix_reminder_schedules_boleto_id", "reminder_schedules", ["boleto_id"])
    op.create_index("ix_reminder_schedules_status", "reminder_schedules", ["status"])


def downgrade() -> None:
    op.drop_index("ix_reminder_schedules_status", table_name="reminder_schedules")
    op.drop_index("ix_reminder_schedules_boleto_id", table_name="reminder_schedules")
    op.drop_index("ix_reminder_schedules_tenant_id", table_name="reminder_schedules")
    op.drop_table("reminder_schedules")

    op.drop_index("ix_interest_policies_tenant_id", table_name="interest_policies")
    op.drop_table("interest_policies")

    reminder_status_enum = postgresql.ENUM(
        "pending", "sent", "cancelled",
        name="reminder_status_enum",
    )
    reminder_status_enum.drop(op.get_bind(), checkfirst=True)
