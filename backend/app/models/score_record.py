from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ScoreRecord(Base):
    __tablename__ = "score_records"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    org: Mapped[str] = mapped_column(String(200), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scoring_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_pdf_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_pdf_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    document_text: Mapped[str] = mapped_column(Text, nullable=False)
    transcript_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    rubric_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    llm_raw_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    result_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False, default="")
    export_markdown_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    export_pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
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
