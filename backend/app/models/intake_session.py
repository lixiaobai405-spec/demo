from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AssessmentIntakeSession(Base):
    __tablename__ = "assessment_intake_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    structured_fields_payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    parsed_payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    normalized_payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_assessment_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
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
