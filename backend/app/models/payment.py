from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PaymentOrder(Base):
    __tablename__ = "payment_orders"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    assessment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assessments.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="CNY")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    qr_code_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_transaction_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AssessmentEntitlement(Base):
    __tablename__ = "assessment_entitlements"
    __table_args__ = (
        UniqueConstraint("assessment_id", "user_id", name="uq_assessment_entitlements_assessment_user"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    assessment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assessments.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    unlock_type: Mapped[str] = mapped_column(String(50), nullable=False, default="paid_assessment")
    source_order_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("payment_orders.id"), nullable=True
    )
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
