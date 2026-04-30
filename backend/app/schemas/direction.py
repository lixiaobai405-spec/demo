from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DirectionSuggestion(BaseModel):
    direction_id: str
    element_key: str
    title: str
    description: str
    expected_impact: str
    data_needed: list[str] = Field(default_factory=list)
    related_scenario_categories: list[str] = Field(default_factory=list)


class DirectionExpansionByElement(BaseModel):
    element_key: str
    element_title: str
    suggestions: list[DirectionSuggestion] = Field(default_factory=list)


class DirectionExpansionResult(BaseModel):
    generation_mode: Literal["rule_based"]
    elements: list[DirectionExpansionByElement] = Field(default_factory=list)
    total_suggestions: int


class DirectionSelectionRequest(BaseModel):
    selected_direction_ids: list[str] = Field(min_length=1, max_length=6)


class DirectionSelectionResponse(BaseModel):
    assessment_id: str
    generation_mode: Literal["rule_based"]
    selected_directions: list[DirectionSuggestion] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AssessmentDirectionResponse(BaseModel):
    assessment_id: str
    direction_expansion: DirectionExpansionResult
    direction_selection: DirectionSelectionResponse | None = None


ELEMENT_DIRECTION_LIBRARY: dict[str, list[tuple[str, str, str, list[str], list[str]]]] = {
    "key_partnerships": [
        (
            "partnership_data_sharing",
            "合作伙伴数据协同",
            "与核心合作伙伴建立数据共享机制，打通进销存、售后和市场反馈，提升协同效率。",
            "缩短跨组织响应周期 20-40%，减少信息不对称造成的损失。",
            ["合作伙伴名录", "协同交易数据", "合作 SLA 条款"],
            ["销售增长", "交付运营"],
        ),
        (
            "partnership_ecosystem_expansion",
            "生态伙伴拓展与运营",
            "基于当前业务阶段，系统识别和评估潜在生态伙伴，设计合作机制。",
            "拓展新的增长飞轮，降低获客和交付的单边依赖。",
            ["现有客户与渠道数据", "行业生态地图", "竞品合作模式"],
            ["销售增长", "知识管理"],
        ),
        (
            "partnership_risk_early_warning",
            "供应链/伙伴风险预警",
            "利用交易和履约数据，对关键伙伴的供应稳定性、质量波动和履约风险进行预警。",
            "减少突发断供和质量波动带来的营收冲击。",
            ["供应链历史数据", "履约记录", "质量抽检数据"],
            ["交付运营", "生产运营"],
        ),
    ],
    "key_activities": [
        (
            "activity_process_mining",
            "业务流程挖掘与优化",
            "基于系统日志和工单数据，自动还原实际业务流程，识别瓶颈和冗余环节。",
            "缩短核心流程周期 15-30%，释放管理带宽。",
            ["工单/审批流数据", "流程节点时间戳", "岗位操作记录"],
            ["交付运营", "生产运营"],
        ),
        (
            "activity_sop_automation",
            "SOP 标准化与智能辅助",
            "将核心业务活动的标准作业流程沉淀为知识模型，结合 AI 做实时辅助和异常提示。",
            "降低对个人经验的依赖，新人上手周期缩短 30-50%。",
            ["当前 SOP 文档", "异常处理记录", "岗位操作手册"],
            ["知识管理", "售前效率"],
        ),
        (
            "activity_cross_dept_collaboration",
            "跨部门协同流程设计",
            "围绕端到端交付流程，重新设计销售-交付-售后的协同机制，减少交接损耗。",
            "降低跨部门协同摩擦成本，提升端到端交付满意度。",
            ["跨部门流程现状描述", "协同痛点记录", "组织架构信息"],
            ["交付运营", "销售增长"],
        ),
    ],
    "key_resources": [
        (
            "resource_data_asset_mapping",
            "数据资产盘点与治理",
            "系统梳理企业现有数据资产，建立数据目录、质量评估和治理规则。",
            "为后续所有 AI 场景提供可靠的数据底座。",
            ["系统清单", "数据库/表结构", "数据字典"],
            ["知识管理", "生产运营"],
        ),
        (
            "resource_knowledge_graph",
            "企业知识图谱构建",
            "将分散在文档、系统和人员中的知识结构化，形成可检索、可推理的企业知识图谱。",
            "知识检索效率提升 60-80%，减少重复调研和沟通成本。",
            ["技术文档", "产品资料", "故障/解决记录"],
            ["知识管理", "售前效率"],
        ),
        (
            "resource_talent_skill_matching",
            "人才技能匹配与梯队建设",
            "结合项目需求和人员技能画像，智能匹配项目组和培训建议。",
            "提升人岗匹配度，降低关键人员流失风险。",
            ["员工技能档案", "项目需求描述", "培训记录"],
            ["客户服务", "知识管理"],
        ),
        (
            "resource_tech_debt_assessment",
            "技术债务评估与系统升级路径",
            "对现有 IT 系统做健康度评估，识别技术债务和升级优先级。",
            "避免老旧系统成为 AI 推进的瓶颈，确保技术架构可扩展。",
            ["系统架构文档", "运维记录", "系统年龄与技术栈"],
            ["生产运营", "交付运营"],
        ),
    ],
    "value_propositions": [
        (
            "vp_differentiation_analysis",
            "差异化竞争力分析",
            "基于行业数据和竞品信息，系统分析企业在价值主张维度的差异化优势与不足。",
            "明确核心竞争力定位，指导 AI 投资方向。",
            ["竞品信息", "客户反馈", "行业报告"],
            ["销售增长", "客户服务"],
        ),
        (
            "vp_personalization_engine",
            "个性化价值交付",
            "基于客户画像和交易历史，为不同客户群体定制差异化的价值组合和服务方案。",
            "提升客户感知价值，客单价和复购率有望改善。",
            ["客户画像数据", "交易历史", "产品/服务配置"],
            ["客户服务", "销售增长"],
        ),
        (
            "vp_value_communication",
            "价值主张传播与量化",
            "将抽象的价值主张转化为可量化、可传播的客户案例和效果数据。",
            "提升市场传播效率和客户信任度。",
            ["客户成功案例", "效果数据", "传播渠道"],
            ["销售增长", "知识管理"],
        ),
    ],
    "customer_relationships": [
        (
            "cr_customer_health_scoring",
            "客户健康度评分",
            "基于交易频率、服务工单、反馈情绪等多维数据，对客户健康度进行动态评分。",
            "提前识别流失风险客户，主动干预。",
            ["交易数据", "服务工单", "客户反馈"],
            ["客户服务", "销售增长"],
        ),
        (
            "cr_intelligent_upsell",
            "智能增购与交叉销售",
            "基于客户使用行为和需求特征，推荐个性化增购和交叉销售方案。",
            "提升客单价和客户生命周期价值。",
            ["客户购买历史", "产品使用数据", "客户需求偏好"],
            ["销售增长", "客户服务"],
        ),
        (
            "cr_community_operations",
            "客户社群运营",
            "搭建行业客户社群，利用 AI 做内容推荐、话题引导和需求捕捉。",
            "从交易关系升级为社区关系，提升粘性和转介绍。",
            ["客户行业分类", "社群平台", "内容素材"],
            ["客户服务", "销售增长"],
        ),
    ],
    "channels": [
        (
            "channel_performance_analytics",
            "渠道效能分析",
            "对各渠道的获客成本、转化周期和客户质量进行系统分析，优化渠道组合。",
            "降低综合获客成本 10-25%，提升渠道 ROI。",
            ["渠道来源标签", "转化链路数据", "渠道成本数据"],
            ["销售增长", "客户服务"],
        ),
        (
            "channel_digital_experience",
            "全渠道数字化体验",
            "统一线上线下客户触点，构建一致性的品牌体验和客户旅程。",
            "提升客户体验一致性，减少渠道间摩擦。",
            ["各渠道触点清单", "客户旅程地图", "触点交互数据"],
            ["客户服务", "销售增长"],
        ),
        (
            "channel_partner_enablement",
            "渠道伙伴赋能",
            "为渠道伙伴提供智能化的销售工具、内容支持和业绩分析。",
            "提升渠道伙伴产出，降低渠道管理成本。",
            ["伙伴清单", "伙伴业绩数据", "销售工具包"],
            ["销售增长", "知识管理"],
        ),
    ],
    "customer_segments": [
        (
            "segment_ai_clustering",
            "AI 客户聚类与分群",
            "基于行为、价值和需求多维数据，自动发现客户细分群体和迁移趋势。",
            "客户细分更精准，营销和产品策略更有针对性。",
            ["客户行为数据", "交易数据", "客户属性数据"],
            ["客户服务", "销售增长"],
        ),
        (
            "segment_ltv_prediction",
            "客户生命周期价值预测",
            "基于历史和当前行为数据，预测客户未来价值和流失概率。",
            "资源投放更有依据，ROI 可量化追踪。",
            ["客户交易历史", "服务记录", "客户行为日志"],
            ["销售增长", "客户服务"],
        ),
        (
            "segment_new_market_identification",
            "新细分市场识别",
            "结合行业趋势和企业能力，系统扫描和评估潜在的新细分市场机会。",
            "开拓新增长空间，降低对存量市场的过度依赖。",
            ["行业报告", "竞品分析", "企业能力矩阵"],
            ["销售增长", "知识管理"],
        ),
    ],
    "cost_structure": [
        (
            "cost_ai_roi_modeling",
            "AI 项目 ROI 建模",
            "对候选 AI 项目进行成本投入与预期收益建模，辅助管理层排序决策。",
            "AI 投资决策更有依据，避免盲目上马。",
            ["项目估算数据", "历史项目成本", "业务指标基线"],
            ["生产运营", "交付运营"],
        ),
        (
            "cost_process_automation",
            "流程自动化降本",
            "识别高频、低决策量的流程节点，优先推进 RPA 或智能自动化。",
            "直接降低人工运营成本，释放人员做更高价值工作。",
            ["流程清单与耗时", "人工成本数据", "系统接口情况"],
            ["生产运营", "交付运营"],
        ),
        (
            "cost_resource_optimization",
            "资源利用率优化",
            "基于业务波动数据，动态优化人员、设备和物料等资源的调配。",
            "提升资源利用率 10-20%，降低闲置和加班成本。",
            ["资源使用数据", "业务量波动数据", "资源成本数据"],
            ["生产运营", "交付运营"],
        ),
    ],
    "revenue_streams": [
        (
            "revenue_pricing_optimization",
            "动态定价与收益优化",
            "基于市场、库存和客户数据，优化产品或服务的定价策略。",
            "在不损失竞争力的前提下，提升整体毛利率。",
            ["历史定价数据", "成交价格", "竞品价格"],
            ["销售增长", "生产运营"],
        ),
        (
            "revenue_subscription_model",
            "订阅/服务化收入转型",
            "探索从一次性销售向订阅制或服务化收费模式的转型路径。",
            "构建更稳定、可预测的经常性收入结构。",
            ["客户使用模式", "服务成本数据", "行业订阅案例"],
            ["销售增长", "客户服务"],
        ),
        (
            "revenue_new_business_line",
            "新业务线孵化评估",
            "基于企业核心能力和市场机会，系统评估新业务线的可行性和优先级。",
            "开拓第二增长曲线，降低单一收入来源风险。",
            ["行业趋势报告", "企业能力评估", "市场调研数据"],
            ["销售增长", "知识管理"],
        ),
    ],
}
