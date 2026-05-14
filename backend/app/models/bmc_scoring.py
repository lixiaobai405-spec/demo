"""BMC 三维评分 — 数据库模型"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from app.db.session import Base


class BMCScoring(Base):
    __tablename__ = "bmc_scorings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    assessment_id = Column(
        String(36),
        ForeignKey("assessments.id"),
        unique=True,
        index=True,
        nullable=False,
    )
    module_scores_json = Column(Text, nullable=False, default="[]")
    scoring_result_json = Column(Text, nullable=False, default="{}")
    selected_keys_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
