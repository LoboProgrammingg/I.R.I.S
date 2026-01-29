"""Fix users.tenant_id FK from CASCADE to RESTRICT.

Revision ID: 002
Revises: 001
Create Date: 2026-01-29

Reason:
- CASCADE delete is unsafe for financial systems
- Deleting a tenant should NOT automatically delete users
- Explicit handling required to prevent accidental data loss

Change:
- Drop FK `fk_users_tenant_id` with ON DELETE CASCADE
- Recreate FK `fk_users_tenant_id` with ON DELETE RESTRICT

Rollback: Reverts to CASCADE (original behavior)
"""

from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing CASCADE FK
    op.drop_constraint("fk_users_tenant_id", "users", type_="foreignkey")

    # Recreate FK with RESTRICT
    op.create_foreign_key(
        constraint_name="fk_users_tenant_id",
        source_table="users",
        referent_table="tenants",
        local_cols=["tenant_id"],
        remote_cols=["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    # Drop RESTRICT FK
    op.drop_constraint("fk_users_tenant_id", "users", type_="foreignkey")

    # Recreate FK with CASCADE (original)
    op.create_foreign_key(
        constraint_name="fk_users_tenant_id",
        source_table="users",
        referent_table="tenants",
        local_cols=["tenant_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
