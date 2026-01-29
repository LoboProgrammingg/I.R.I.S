"""Add tenants and users tables for Identity & Tenancy bounded context.

Revision ID: 001
Revises: None
Create Date: 2026-01-29

Schema:
- tenants: Logical customer/account that owns all data
- users: Human operators within a tenant

Invariants enforced:
- Tenant ID is primary key (immutable)
- User ID is primary key (immutable)
- Phone number unique within tenant (uq_users_tenant_phone)
- User must belong to exactly one tenant (fk_users_tenant_id)
- Cascade delete: users deleted when tenant deleted

Rollback: Safe, drops tables in correct order (users first, then tenants)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_role_enum type
    user_role_enum = postgresql.ENUM("admin", "user", name="user_role_enum")
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Create tenants table
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
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
    )

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM("admin", "user", name="user_role_enum", create_type=False),
            nullable=False,
            server_default="user",
        ),
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
            name="fk_users_tenant_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("tenant_id", "phone_number", name="uq_users_tenant_phone"),
    )

    # Create index for tenant_id lookups
    op.create_index(
        "ix_users_tenant_id",
        "users",
        ["tenant_id"],
    )


def downgrade() -> None:
    # Drop users table first (has FK to tenants)
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_table("users")

    # Drop tenants table
    op.drop_table("tenants")

    # Drop enum type
    user_role_enum = postgresql.ENUM("admin", "user", name="user_role_enum")
    user_role_enum.drop(op.get_bind(), checkfirst=True)
