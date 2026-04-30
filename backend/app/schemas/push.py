from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TaskStatus = Literal["pending", "in_progress", "completed", "blocked"]


class PushedCase(BaseModel):
    case_id: str
    title: str
    industry: str
    summary: str
    fit_score: int = Field(ge=0, le=100)
    source_summary: str = ""
    reference_points: list[str] = Field(default_factory=list)
    data_foundation: list[str] = Field(default_factory=list)
    cautions: list[str] = Field(default_factory=list)


class PushCycleResult(BaseModel):
    cycle: int
    pushed_cases: list[PushedCase] = Field(default_factory=list)
    cycle_note: str = ""
    pushed_at: datetime | None = None
    previous_case_ids: list[str] = Field(default_factory=list)
    total_available: int = 0


class RecalibrateActionItem(BaseModel):
    task_id: str | None = None
    period: str | None = None
    action: str = ""
    owner_suggestion: str = ""
    deliverable: str = ""
    status: TaskStatus = "pending"


class RecalibratePlanRequest(BaseModel):
    note: str = Field(min_length=1, max_length=500)
    new_actions: list[RecalibrateActionItem] = Field(default_factory=list)
    update_task_ids: list[str] = Field(default_factory=list)


def _build_cycle_note(cycle: int) -> str:
    notes = {
        1: '第 1-2 周：聚焦案例中的\u201c快速验证\u201d思路，检查自己的试点是否在正确的路径上。',
        2: '第 3-4 周：对比案例中的\u201c规模化\u201d做法，评估是否需要调整扩展策略。',
        3: '第 5-6 周：学习案例中的\u201c生态协同\u201d经验，思考建立平台效应的可能性。',
        4: '第 7-8 周：参考案例中的\u201c组织变革\u201d方法，推动内部能力建设与人才梯队。',
        5: '第 9-10 周：结合案例中的\u201c商业终局\u201d案例，重新审视长期战略路径。',
        6: '第 11-12 周：汇总历史推送案例，形成完整的对标学习报告。',
    }
    return notes.get(cycle, f'第 {cycle} 轮推送：持续关注行业最佳实践，结合自身进展调整方案。')
