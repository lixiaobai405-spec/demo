from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    assessment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("assessments.id"),
        nullable=False,
        unique=True,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    generation_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    used_llm: Mapped[bool] = mapped_column(default=False, nullable=False)
    used_rag: Mapped[bool] = mapped_column(default=False, nullable=False)
    warnings: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_json: Mapped[str] = mapped_column("report_json", Text, nullable=False)
    export_markdown_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    export_docx_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
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
