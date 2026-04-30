from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class BreakthroughSelection(Base):
    __tablename__ = "breakthrough_selections"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    assessment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("assessments.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    selection_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    recommended_elements_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    selected_elements_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
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
