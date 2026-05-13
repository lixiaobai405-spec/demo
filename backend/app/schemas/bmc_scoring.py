"""
BMC（三维）评分相关 Schema。

该模块用于“突破要素评分”能力：根据用户对商业画布九要素的三维评分（痛点/数据/可行性）
计算每个模块的推荐级别与 Top3，并支持保存与查询。
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ModuleScoreInput(BaseModel):
    """单个 BMC 模块的输入分值（由前端传入或后端自动推导）。"""

    key: str = Field(..., description="模块键（如 customer_segments/value_propositions 等）")
    pain: int = Field(..., ge=0, le=5, description="痛点强度（0-5）")
    data: int = Field(..., ge=0, le=5, description="数据可得性（0-5）")
    feasibility: int = Field(..., ge=0, le=5, description="落地可行性（0-5）")


BmcScoringZone = Literal["quickwin", "strategic", "longterm", "hold", "blocked"]


class ModuleScoringResult(BaseModel):
    """单个 BMC 模块的评分结果（供前端可视化与选择）。"""

    key: str
    title: str
    abbr: str
    category: str

    pain: int
    data: int
    feasibility: int

    raw_score: float
    normalized_score: float
    zone: BmcScoringZone

    veto_status: str
    veto_reason: str | None = None

    recommendation_level: str
    recommendation_label: str
    recommendation_stars: str


class BmcScoringResult(BaseModel):
    """一次 BMC 三维评分的整体结果（含 Top3）。"""

    assessment_id: str
    module_results: list[ModuleScoringResult]
    top_3_keys: list[str]
    top_3_results: list[ModuleScoringResult]
    complementarity_warning: str | None = None


class BmcScoringSaveRequest(BaseModel):
    """保存 BMC 评分选择结果的请求体。"""

    selected_keys: list[str] = Field(default_factory=list, description="用户最终确认的 Top3 模块 key")
    all_module_scores: list[ModuleScoreInput] = Field(default_factory=list, description="所有模块的输入分值")
    selection_mode: Literal["bmc_scoring", "manual"] = Field(
        default="manual",
        description="选择模式：bmc_scoring=按评分推荐；manual=手动选择",
    )


class BmcScoringResponse(BaseModel):
    """查询/保存 BMC 评分的响应体。"""

    assessment_id: str
    scoring_result: BmcScoringResult | None
    selected_keys: list[str]
    created_at: str | None = None
    updated_at: str | None = None


class AutoDeriveResponse(BaseModel):
    """从商业画布自动推导模块分值的响应体（可先返回默认值，便于 Demo 跑通）。"""

    modules: list[ModuleScoreInput]
    derived_from_canvas: bool

