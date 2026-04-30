from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TaskStatus = Literal["pending", "in_progress", "completed", "blocked"]


class FollowUpTaskItem(BaseModel):
    task_id: str
    period: str
    action: str
    owner_suggestion: str
    deliverable: str
    status: TaskStatus = "pending"
    progress_note: str | None = None
    blocked: bool = False
    blocker_description: str | None = None
    sort_order: int = 0
    last_reviewed_at: datetime | None = None


class FollowUpPlan(BaseModel):
    assessment_id: str
    tasks: list[FollowUpTaskItem] = Field(default_factory=list)
    overall_progress_pct: int = 0
    completed_count: int = 0
    blocked_count: int = 0
    total_count: int = 0
    next_review_date: str | None = None
    recalibration_note: str | None = None


class TaskUpdateRequest(BaseModel):
    status: TaskStatus | None = None
    progress_note: str | None = None
    blocked: bool | None = None
    blocker_description: str | None = None


class RecalibrateRequest(BaseModel):
    note: str = Field(min_length=1, max_length=500)
    updated_tasks: list[dict] = Field(default_factory=list)


DEFAULT_FOLLOW_UP_TASKS = [
    {
        "period": "第 1-15 天",
        "action": "确认 AI 试点项目的核心参与人、项目范围和可量化目标。",
        "owner_suggestion": "项目经理 / 业务负责人",
        "deliverable": "试点立项书（含目标、范围、人员、数据源）",
    },
    {
        "period": "第 1-15 天",
        "action": "完成数据盘点和数据质量评估，确定可用于 AI 试点的最小数据底座。",
        "owner_suggestion": "数据 / IT 负责人",
        "deliverable": "数据资产评估报告",
    },
    {
        "period": "第 16-30 天",
        "action": "启动第一个 AI 试点场景的 PoC 开发或低代码验证。",
        "owner_suggestion": "技术负责人 + 业务骨干",
        "deliverable": "PoC 可运行版本 + 首轮验证结论",
    },
    {
        "period": "第 16-30 天",
        "action": "建立周复盘机制，记录试点过程中的关键发现、数据问题和用户反馈。",
        "owner_suggestion": "项目经理",
        "deliverable": "每周复盘纪要（至少 2 次）",
    },
    {
        "period": "第 31-45 天",
        "action": "基于首轮验证调整方案，准备扩展到第 2 个试点场景或扩大试点范围。",
        "owner_suggestion": "项目经理 + 业务负责人",
        "deliverable": "试点迭代方案 + 扩展评估",
    },
    {
        "period": "第 31-45 天",
        "action": "完成 30 天试点效果评估，向管理层汇报阶段性结论和下一步投资建议。",
        "owner_suggestion": "项目经理",
        "deliverable": "30 天复盘报告 + 下一阶段立项建议",
    },
]
