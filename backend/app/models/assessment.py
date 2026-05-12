from datetime import datetime, timezone
from uuid import uuid4

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.user import User


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(255), nullable=False)
    company_size: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(255), nullable=False)
    annual_revenue_range: Mapped[str] = mapped_column(String(100), nullable=False)
    core_products: Mapped[str] = mapped_column(Text, nullable=False)
    target_customers: Mapped[str] = mapped_column(Text, nullable=False)
    current_challenges: Mapped[str] = mapped_column(Text, nullable=False)
    ai_goals: Mapped[str] = mapped_column(Text, nullable=False)
    available_data: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True, index=True
    )
    class_group: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instructor_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_generation_mode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    profile_generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
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

    user: Mapped["User | None"] = relationship("User", back_populates="assessments")

    @property
    def has_profile(self) -> bool:
        return bool(self.profile_payload)

