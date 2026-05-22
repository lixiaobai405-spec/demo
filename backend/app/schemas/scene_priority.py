"""Top 3 AI 场景推荐 · 四象限优先级评分 — Pydantic Schema

对应 PRD: ALGO-SCENE-SCORE-001
"""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════
# 枚举定义
# ═══════════════════════════════════════════

class Quadrant(str, Enum):
    ai_priority = "AI优先区"
    automation_battlefield = "自动化主战场"
    human_ai_collab = "人机协作区"
    human_reserved = "人类保留区"


class RecommendationLevel(str, Enum):
    immediate_start = "立即启动"    # LPS_display >= 8.0
    plan_advance = "规划推进"       # 5.0 <= LPS_display < 8.0
    observe = "观察"               # LPS_display < 5.0


# ═══════════════════════════════════════════
# 算法常量
# ═══════════════════════════════════════════

QUADRANT_THRESHOLD = 3.5
WEIGHT_X = 0.6
WEIGHT_Y_INV = 0.4
Y_INVERSION_BASE = 6
LPS_DISPLAY_MULTIPLIER = 2

# 推荐等级阈值
IMMEDIATE_START_THRESHOLD = 8.0
PLAN_ADVANCE_THRESHOLD = 5.0

# 规则 C：自动化主战场替换容忍度
AUTO_REPLACEMENT_TOLERANCE = 1.0


# ═══════════════════════════════════════════
# NLP 自动评分信号词典
# ═══════════════════════════════════════════

STRUCTUREDNESS_SIGNALS: dict[int, list[str]] = {
    5: ["系统里都有", "ERP记录", "标准流程", "每步都有数据", "SOP完善",
        "全程数字化", "完整数据库", "自动记录", "系统化管理"],
    4: ["大部分有记录", "Excel汇总", "规则比较清晰", "偶有例外",
        "数据较完整", "流程规范", "有标准模板"],
    3: ["部分有记录", "流程不太统一", "经验和系统都有用",
        "有一定数据", "半结构化", "部分数字化"],
    2: ["全靠经验", "老师傅知道", "比较灵活", "每次都不一样",
        "数据零散", "主要靠人", "难以标准化"],
    1: ["说不清楚规律", "完全凭感觉", "人与人差距很大", "无法量化",
        "纯手工", "无系统记录"],
}

COMPLEXITY_SIGNALS: dict[int, list[str]] = {
    5: ["多变量", "高阶分析", "深度专业判断", "错误代价极高",
        "战略决策", "需要资深专家", "跨领域知识"],
    4: ["跨领域", "较强专业背景", "情境判断", "综合分析",
        "需要专家经验", "涉及多部门", "非线性决策"],
    3: ["多变量", "标准化路径", "一定专业知识", "可遵循流程",
        "综合分析", "需要经验积累"],
    2: ["少量变量", "线性逻辑", "规则可描述", "专业要求不高",
        "简单判断", "标准操作"],
    1: ["简单重复", "完全固定", "无需判断", "纯机械化",
        "一键操作", "定时任务"],
}


# ═══════════════════════════════════════════
# 行业修正系数
# ═══════════════════════════════════════════

INDUSTRY_COEFFICIENTS: dict[str, float] = {
    # PRD §3.3 原始 6 行映射。按键长度降序存储以便最长键优先匹配。
    "制造业（流程型）": 1.03,
    "制造业（离散型）": 1.00,
    "专业服务业": 0.95,
    "公共服务": 0.92,
    "高监管行业": 0.90,
    "数字科技": 1.05,
    "互联网": 1.05,
    "医疗": 0.90,
    "物业": 0.92,
}

DEFAULT_INDUSTRY_COEFFICIENT = 1.00


# ═══════════════════════════════════════════
# 输入模型
# ═══════════════════════════════════════════

class ScenePriorityInput(BaseModel):
    """单个候选场景的优先级评分输入"""
    scene_id: str
    scene_name: str
    category: str
    summary: str
    structuredness_x: float = Field(ge=1, le=5, description="结构化程度 1-5")
    complexity_y: float = Field(ge=1, le=5, description="任务复杂程度 1-5")
    industry: str = ""
    canvas_elements: str = ""
    expected_effects: str = ""
    core_data_requirements: str = ""
    # 新版结构化字段
    canvas_element: str = ""
    canvas_key: str = ""
    positioning: str = ""
    value_dimensions: list[str] = Field(default_factory=list)
    value_text: str = ""
    benefits: list[dict] = Field(default_factory=list)
    resources: list[dict] = Field(default_factory=list)


class ScenePriorityScore(BaseModel):
    """单个场景的完整四象限评分结果"""
    scene_id: str
    scene_name: str
    category: str
    structuredness_x: float
    complexity_y: float
    qs: float = Field(description="象限定位得分 QS = X × Y")
    lps: float = Field(description="落地优先级 LPS = X×0.6 + (6-Y)×0.4")
    lps_display: float = Field(description="UI 展示分 LPS_display = LPS × κ × 2（PRD §3.3）")
    lps_final: float = Field(description="行业修正后中间值 LPS × κ")
    industry_coefficient: float = Field(default=1.0, description="行业修正系数 κ")
    quadrant: Quadrant
    priority_tier: int = Field(ge=1, le=4, description="推荐梯队 1-4")
    recommendation_level: RecommendationLevel
    recommendation_label: str = ""
    recommendation_template: str = ""
    rank: int | None = Field(default=None, description="推荐排名 1-3（🥇🥈🥉），仅 Top 3 有值")


# ═══════════════════════════════════════════
# 输出模型
# ═══════════════════════════════════════════

class ScenePriorityResult(BaseModel):
    """Top 3 场景优先级评分完整结果"""
    scoring_method: Literal["four_quadrant_v1"] = "four_quadrant_v1"
    total_candidates: int
    eligible_count: int
    all_scores: list[ScenePriorityScore] = Field(default_factory=list)
    top_3: list[ScenePriorityScore] = Field(default_factory=list)
    fallback_triggered: bool = False
    fallback_reason: str = ""


# ═══════════════════════════════════════════
# 推荐话术模板
# ═══════════════════════════════════════════

QUADRANT_RECOMMENDATION_TEMPLATES: dict[Quadrant, str] = {
    Quadrant.automation_battlefield: (
        "✅ 强烈推荐 · 快速启动 | "
        "该场景具备'高结构化+低实施复杂度'的黄金组合，"
        "是AI落地成功率最高、见效最快的切入点。"
        "建议作为AI转型的第一个实战项目，3个月内即可见到可量化效果。"
    ),
    Quadrant.ai_priority: (
        "⭐ 高价值推荐 · 战略必争 | "
        "该场景AI替代价值极高（高复杂度人工代价大），且流程已具备数字化基础。"
        "实施周期相对较长，但一旦完成，将形成竞争对手难以复制的AI竞争壁垒。"
    ),
    Quadrant.human_ai_collab: (
        "⚠️ 有条件推荐 · 人机协同 | "
        "该场景结构化程度相对较低，AI无法完全替代人工判断，"
        "但AI可以显著提升人类决策的质量和速度。"
        "推荐采用'AI辅助+专家决策'的协同模式推进。"
    ),
    Quadrant.human_reserved: (
        "⚠️ 此场景当前不适合AI直接替代，建议先做数据基础建设"
    ),
}
