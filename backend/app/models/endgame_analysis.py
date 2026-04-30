from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class EndgameAnalysis(Base):
    __tablename__ = "endgame_analyses"

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
    private_domain_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    ecosystem_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    opc_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    strategic_paths_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    overall_narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
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
