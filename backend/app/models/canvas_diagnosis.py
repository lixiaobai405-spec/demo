from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CanvasDiagnosis(Base):
    __tablename__ = "canvas_diagnoses"

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
    generation_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    canvas_json: Mapped[str] = mapped_column(Text, nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    weakest_blocks: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_focus: Mapped[str] = mapped_column(Text, nullable=False)
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
