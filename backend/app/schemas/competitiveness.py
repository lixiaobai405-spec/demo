from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class VPReconstruction(BaseModel):
    current_vp: str
    enhanced_vp: str
    differentiation_points: list[str] = Field(default_factory=list)
    customer_value_shift: str


class PointToLineConnection(BaseModel):
    line_name: str
    point_ids: list[str] = Field(default_factory=list)
    point_titles: list[str] = Field(default_factory=list)
    strategic_narrative: str
    competitive_impact: str
    key_metrics: list[str] = Field(default_factory=list)


class CoreAdvantage(BaseModel):
    advantage_name: str
    source_elements: list[str] = Field(default_factory=list)
    description: str
    barrier_level: Literal["低", "中", "高"]


class DeliveryStrategy(BaseModel):
    phase_1_quick_win: str
    phase_2_scale: str
    phase_3_moat: str
    key_risks: list[str] = Field(default_factory=list)


class CompetitivenessResult(BaseModel):
    generation_mode: Literal["rule_based"]
    vp_reconstruction: VPReconstruction
    connections: list[PointToLineConnection] = Field(default_factory=list)
    advantages: list[CoreAdvantage] = Field(default_factory=list)
    delivery_strategy: DeliveryStrategy
    overall_narrative: str


class CompetitivenessResponse(BaseModel):
    assessment_id: str
    result: CompetitivenessResult
    created_at: datetime | None = None
    updated_at: datetime | None = None


COMPETITIVENESS_KNOWLEDGE = {
    "line_templates": {
        "客户响应速度线": {
            "description": "从客户洞察到快速响应的端到端能力闭环",
            "impact": "缩短从需求识别到价值交付的周期，提升客户满意度和复购率",
            "metrics": ["需求响应周期", "客户满意度", "复购率", "商机转化时间"],
        },
        "数据驱动运营线": {
            "description": "将分散数据资产转化为可行动的业务洞察",
            "impact": "降低决策主观性，提升资源投放 ROI",
            "metrics": ["数据口径统一率", "决策响应时间", "运营成本变化", "异常预警准确率"],
        },
        "知识沉淀复用线": {
            "description": "从个人经验到组织能力的系统化转型",
            "impact": "降低关键人依赖，缩短新人上手周期，提升交付一致性",
            "metrics": ["知识调用率", "新人上手周期", "交付质量方差", "重复问题发生率"],
        },
        "客户关系深化线": {
            "description": "从单次交易到持续客户价值经营",
            "impact": "提升客户生命周期价值，降低获客依赖",
            "metrics": ["客户 LTV", "增购率", "续约率", "客户流失预警准确率"],
        },
        "供应链/交付韧性线": {
            "description": "从被动响应到主动预警的交付能力升级",
            "impact": "降低交付波动，提升供应链透明度和协同效率",
            "metrics": ["订单履约率", "交付周期波动", "异常响应时间", "库存周转率"],
        },
    },
    "category_to_line": {
        "销售增长": ["客户响应速度线", "客户关系深化线"],
        "交付运营": ["供应链/交付韧性线", "数据驱动运营线"],
        "客户服务": ["客户响应速度线", "客户关系深化线"],
        "知识管理": ["知识沉淀复用线", "数据驱动运营线"],
        "生产运营": ["供应链/交付韧性线", "数据驱动运营线"],
        "售前效率": ["客户响应速度线", "知识沉淀复用线"],
    },
    "vp_enhancement_templates": {
        "key_partnerships": "强化生态协同网络",
        "key_activities": "构建端到端流程智能化能力",
        "key_resources": "将数据与知识资产化为核心竞争力",
        "value_propositions": "从产品交付升级为价值共创",
        "customer_relationships": "从交易关系深化为战略伙伴关系",
        "channels": "打造全渠道智能触达体系",
        "customer_segments": "实现精准分群与个性化价值交付",
        "cost_structure": "构建弹性成本与智能资源调度体系",
        "revenue_streams": "探索服务化收入与订阅式商业模式",
    },
}
