from typing import Literal

from pydantic import BaseModel, Field


class PrivateDomainDesign(BaseModel):
    current_state: str
    target_model: str
    key_strategies: list[str] = Field(default_factory=list)
    customer_retention_loop: str
    revenue_impact: str


class EcosystemDesign(BaseModel):
    ecosystem_positioning: str
    key_partners_to_engage: list[str] = Field(default_factory=list)
    orchestration_strategy: str
    platform_effect: str


class OPCDesign(BaseModel):
    operations_excellence: str
    platform_capability: str
    content_and_community: str
    data_flywheel_effect: str


class StrategicPath(BaseModel):
    path_name: str
    path_type: Literal["保守", "均衡", "激进"]
    timeline: str
    key_milestones: list[str] = Field(default_factory=list)
    required_investments: str
    expected_outcomes: str
    major_risks: list[str] = Field(default_factory=list)
    recommendation_level: Literal["推荐", "可选", "不推荐"]


class EndgameResult(BaseModel):
    generation_mode: Literal["rule_based", "llm"]
    private_domain: PrivateDomainDesign
    ecosystem: EcosystemDesign
    opc: OPCDesign
    strategic_paths: list[StrategicPath] = Field(default_factory=list)
    overall_narrative: str


class EndgameResponse(BaseModel):
    assessment_id: str
    result: EndgameResult
    created_at: str | None = None
    updated_at: str | None = None


ENDGAME_KNOWLEDGE = {
    "private_domain_templates": {
        "制造": {
            "target_model": "构建以供应链协同为核心的产业私域，通过订单与交付数据打通上下游信息壁垒。",
            "strategies": [
                "建立客户专属数据空间，提供实时库存和交付可视化",
                "围绕关键大客户构建联合计划与预测机制",
                "将售后知识沉淀为可复用的客户自助服务能力",
            ],
            "retention_loop": "数据沉淀 → 需求预判 → 主动服务 → 信任加深 → 更多数据共享",
        },
        "零售": {
            "target_model": "从交易型会员升级为数据驱动的个性化服务型会员体系。",
            "strategies": [
                "整合全渠道触点数据，建立统一客户视图",
                "基于消费行为分群实现精准触达与个性化推荐",
                "搭建会员积分+内容社区的双轮驱动留资模型",
            ],
            "retention_loop": "全渠道触达 → 个性化服务 → 复购提升 → 数据回流 → 更精准的分群",
        },
        "科技": {
            "target_model": "以产品使用数据为纽带，构建客户成功驱动的留存模型。",
            "strategies": [
                "产品健康度监控与主动介入，降低流失风险",
                "基于使用行为的分层服务策略",
                "建立客户成功案例社区，形成口碑传播飞轮",
            ],
            "retention_loop": "产品使用 → 健康诊断 → 主动支持 → 价值认可 → 增购/续约",
        },
        "通用": {
            "target_model": "将分散的客户触点整合为统一的私域运营体系，实现从获客到留客的全链路闭环。",
            "strategies": [
                "梳理全渠道客户触点，建立第一方数据资产",
                "基于客户分层实施差异化运营策略",
                "构建内容+服务+工具三位一体的私域价值体系",
            ],
            "retention_loop": "触点数据化 → 客户分层 → 精准运营 → 价值留存 → 数据资产积累",
        },
    },
    "ecosystem_templates": {
        "制造": {
            "positioning": "作为产业链协同枢纽，连接上游供应商与下游客户的数据和流程。",
            "partners": ["核心供应商", "区域物流服务商", "行业技术平台", "金融服务机构"],
            "orchestration": "以供应链数据中台为核心，构建上下游协同的信息共享与业务联动机制。",
            "platform_effect": "数据网络效应：更多的参与方带来更精准的需求预判和更高效的资源配置。",
        },
        "零售": {
            "positioning": "作为品牌与消费者的价值连接器，整合线上线下全域流量入口。",
            "partners": ["品牌供应商", "物流配送", "内容创作者/KOC", "支付与金融服务"],
            "orchestration": "以消费者数据平台(CDP)为底座，构建人-货-场匹配的智能运营网络。",
            "platform_effect": "双边网络效应：更多消费者吸引更多品牌，更多品牌吸引更多消费者。",
        },
        "科技": {
            "positioning": "作为行业技术基础设施提供者，让合作伙伴在平台之上创新。",
            "partners": ["技术集成商", "ISV/应用开发者", "行业咨询伙伴", "学术研究机构"],
            "orchestration": "提供开放 API 和开发者社区，将核心能力赋能生态伙伴。",
            "platform_effect": "开发者和应用越多，平台价值越大，形成正反馈技术飞轮。",
        },
        "通用": {
            "positioning": "找准产业链中的关键枢纽位置，通过数据与流程连接上下游参与者。",
            "partners": ["核心供应商", "渠道合作伙伴", "技术平台", "行业服务机构"],
            "orchestration": "以关键数据或流程节点为支点，撬动生态协同效应。",
            "platform_effect": "规模+数据双轮驱动：更多参与者带来更多数据和更强的协同效率。",
        },
    },
    "opc_templates": {
        "制造": {
            "operations": "打造端到端订单交付的智能调度中枢，实现需求到生产的快速响应。",
            "platform": "构建供应链数字孪生平台，支撑多级供应商协同与异常预警。",
            "content_community": "沉淀工艺优化和质量管理知识库，赋能一线工程师持续改进。",
            "data_flywheel": "订单/库存/质量数据 → 预测模型 → 调度优化 → 更准需求 → 更多数据。",
        },
        "零售": {
            "operations": "建立全渠道商品和库存的统一运营体系，实现智能选品与动态定价。",
            "platform": "搭建消费者数据平台(CDP)，支撑千人千面的营销与服务体系。",
            "content_community": "构建种草-购买-晒单的内容闭环，形成用户自生长的社群生态。",
            "data_flywheel": "消费者行为数据 → 精准画像 → 个性化推荐 → 更高转化 → 更多行为数据。",
        },
        "科技": {
            "operations": "建立研发效能度量和持续交付体系，实现产品创新与稳定交付的平衡。",
            "platform": "将核心能力 API 化，支撑生态伙伴在平台之上的二次创新。",
            "content_community": "建设开发者社区和知识库，降低接入成本，加速生态扩展。",
            "data_flywheel": "产品使用数据 → 用户洞察 → 产品迭代 → 更高满意度 → 更多使用数据。",
        },
        "通用": {
            "operations": "建立数据驱动的核心业务运营体系，实现关键流程标准化与自动化。",
            "platform": "将已验证能力抽象为可复用的平台服务，支撑多业务线高效运转。",
            "content_community": "构建行业知识资产和用户社区，形成可持续的内容和口碑引擎。",
            "data_flywheel": "业务数据 → 决策模型 → 运营优化 → 更好结果 → 更多数据积累。",
        },
    },
}
