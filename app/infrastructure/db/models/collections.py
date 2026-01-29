"""SQLAlchemy models for Collections bounded context."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models.base import Base


class InterestPolicyModel(Base):
    """InterestPolicy database model."""

    __tablename__ = "interest_policies"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "is_active",
            name="uq_interest_policies_tenant_active",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", name="fk_interest_policies_tenant_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    grace_period_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    daily_interest_rate_bps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    fixed_penalty_cents: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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


class ReminderScheduleModel(Base):
    """ReminderSchedule database model."""

    __tablename__ = "reminder_schedules"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", name="fk_reminder_schedules_tenant_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    boleto_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("boletos.id", name="fk_reminder_schedules_boleto_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "pending", "sent", "cancelled",
            name="reminder_status_enum",
            create_type=True,
        ),
        nullable=False,
        default="pending",
        index=True,
    )
    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
