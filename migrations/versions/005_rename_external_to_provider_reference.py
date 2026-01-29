"""Rename external_id/external_ref to provider_reference.

Revision ID: 005
Revises: 004
Create Date: 2026-01-29

Purpose:
- Standardize provider reference naming across Billing context
- boletos.external_id -> boletos.provider_reference
- payments.external_ref -> payments.provider_reference

Data Safety:
- Uses ALTER TABLE RENAME COLUMN (no data loss)
- No downtime required
- Fully reversible

Rollback: Renames columns back to original names
"""

from typing import Sequence, Union

from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "boletos",
        "external_id",
        new_column_name="provider_reference",
    )
    op.alter_column(
        "payments",
        "external_ref",
        new_column_name="provider_reference",
    )


def downgrade() -> None:
    op.alter_column(
        "boletos",
        "provider_reference",
        new_column_name="external_id",
    )
    op.alter_column(
        "payments",
        "provider_reference",
        new_column_name="external_ref",
    )
