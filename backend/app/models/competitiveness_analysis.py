from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CompetitivenessAnalysis(Base):
    __tablename__ = "competitiveness_analyses"

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
    vp_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    connections_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    advantages_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    strategy_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
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
