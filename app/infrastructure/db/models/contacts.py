"""SQLAlchemy models for Contacts bounded context."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base


class ContactModel(Base):
    """Contact database model.

    Represents a person or entity that can receive boletos and messages.
    Contacts are scoped to exactly one tenant.
    """

    __tablename__ = "contacts"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "phone_number",
            name="uq_contacts_tenant_phone",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", name="fk_contacts_tenant_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    phone_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    opted_out: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    tenant: Mapped["TenantModel"] = relationship(  # noqa: F821
        "TenantModel",
        lazy="selectin",
    )
