"""SQLAlchemy models for Billing bounded context."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base


class BoletoModel(Base):
    """Boleto database model."""

    __tablename__ = "boletos"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_boletos_tenant_idempotency",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", name="fk_boletos_tenant_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", name="fk_boletos_contact_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount_cents: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="BRL",
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "created", "sent", "paid", "overdue", "cancelled",
            name="boleto_status_enum",
            create_type=True,
        ),
        nullable=False,
        default="created",
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    provider_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
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

    payment: Mapped["PaymentModel | None"] = relationship(
        "PaymentModel",
        back_populates="boleto",
        uselist=False,
    )


class PaymentModel(Base):
    """Payment database model."""

    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    boleto_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("boletos.id", name="fk_payments_boleto_id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    amount_cents: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="BRL",
    )
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    provider_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    boleto: Mapped["BoletoModel"] = relationship(
        "BoletoModel",
        back_populates="payment",
    )
