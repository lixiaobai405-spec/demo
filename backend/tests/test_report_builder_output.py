from datetime import datetime, timezone
from pathlib import Path
import sys
from types import SimpleNamespace

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.assessment import (
    BusinessModelCanvasResult,
    CanvasBlockResult,
    CanvasDiagnosisResult,
    CompanyProfileResult,
    ScenarioRecommendationItem,
    ScenarioRecommendationResult,
)
from app.schemas.competitiveness import (
    CompetitivenessResult,
    CoreAdvantage,
    DeliveryStrategy,
    PointToLineConnection,
    VPReconstruction,
)
from app.schemas.endgame import (
    EcosystemDesign,
    EndgameResult,
    OPCDesign,
    PrivateDomainDesign,
    StrategicPath,
    ThreeStageStrategy,
    ThreeStageStrategyStage,
)
from app.services.report_builder import ReportBuilder


def _long_text(prefix: str) -> str:
    """构造会触发旧截断逻辑的长文本样例。"""
    return prefix + "，" + "这是完整内容" * 30


def _build_assessment() -> SimpleNamespace:
    """构造用于报告生成测试的轻量评估对象。"""
    return SimpleNamespace(
        id="assessment-report-builder",
        company_name="测试零售企业",
        industry="零售",
        company_size="100-499人",
        region="华东",
        annual_revenue_range="5000万-1亿元",
        core_products="门店运营与会员服务",
        target_customers="会员用户",
        current_challenges="复购波动",
        ai_goals="提升运营效率",
        available_data="POS、会员系统",
        notes=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def _build_canvas() -> CanvasDiagnosisResult:
    """构造画布诊断样例，覆盖摘要与模块明细。"""
    return CanvasDiagnosisResult(
        generation_mode="mock",
        overall_score=82,
        weakest_blocks=["客户关系", "渠道通路"],
        recommended_focus=["优化客户分层", "统一门店运营标准"],
        canvas=BusinessModelCanvasResult(
            overall_summary=_long_text("商业画布整体判断"),
            blocks=[
                CanvasBlockResult(
                    key="customer_relationships",
                    title="客户关系",
                    current_state=_long_text("当前状态"),
                    diagnosis=_long_text("核心诊断"),
                    ai_opportunity=_long_text("AI 机会"),
                    missing_information="该字段仍保留在内部数据中，但不应出现在报告中。",
                )
            ],
        ),
    )


def _build_profile() -> CompanyProfileResult:
    """构造企业画像样例，避免报告中引入待补充信息文案。"""
    return CompanyProfileResult(
        company_name="测试零售企业",
        company_summary=_long_text("企业概览"),
        value_proposition="围绕门店服务和会员运营提升复购与体验",
        customer_and_market="社区家庭用户与会员客户",
        operations_and_resources="已有 POS、会员系统和巡店记录",
        digital_and_ai_readiness="具备基础数字化系统，可推进业务场景试点",
        key_challenges=["复购波动", "门店经验难复用"],
        priority_ai_directions=["知识沉淀复用", "客户关系深化"],
        missing_information=[],
    )


def _build_scenarios() -> ScenarioRecommendationResult:
    """构造场景推荐样例，覆盖结果页与报告引用内容。"""
    return ScenarioRecommendationResult(
        scoring_method="rule_based_v1",
        evaluated_count=3,
        top_scenarios=[
            ScenarioRecommendationItem(
                scenario_id="scenario-1",
                name="门店知识助手",
                category="运营提效",
                summary=_long_text("场景摘要"),
                score=91,
                reasons=["降低门店培训成本"],
                data_requirements=["POS 数据"],
            )
        ],
    )


def _build_competitiveness() -> CompetitivenessResult:
    """构造竞争力分析样例，覆盖旧省略号文案路径。"""
    return CompetitivenessResult(
        generation_mode="rule_based",
        vp_reconstruction=VPReconstruction(
            current_vp="帮助门店提升经营效率",
            enhanced_vp=_long_text("增强型价值主张"),
            differentiation_points=["知识复用", "客户响应"],
            customer_value_shift=_long_text("客户价值转移"),
        ),
        connections=[
            PointToLineConnection(
                line_name="客户响应速度线",
                point_ids=["direction-1"],
                point_titles=["知识沉淀复用"],
                strategic_narrative=_long_text("战略叙述"),
                competitive_impact="缩短响应周期",
                key_metrics=["客户满意度"],
            )
        ],
        advantages=[
            CoreAdvantage(
                advantage_name="知识复用优势",
                source_elements=["客户关系"],
                description="将门店经验沉淀为组织能力",
                barrier_level="中",
            )
        ],
        delivery_strategy=DeliveryStrategy(
            phase_1_quick_win=_long_text("阶段一策略"),
            phase_2_scale=_long_text("阶段二策略"),
            phase_3_moat=_long_text("阶段三策略"),
            key_risks=["跨部门协同不足"],
        ),
        overall_narrative=_long_text("竞争力总体判断"),
    )


def _build_endgame() -> EndgameResult:
    """构造商业终局样例，覆盖旧截断和量化展示路径。"""
    return EndgameResult(
        generation_mode="rule_based",
        private_domain=PrivateDomainDesign(
            current_state="私域基础薄弱",
            target_model=_long_text("私域目标模型"),
            key_strategies=["统一客户视图"],
            customer_retention_loop="触点数据化 -> 分层运营 -> 价值留存",
            revenue_impact=_long_text("收入影响"),
        ),
        ecosystem=EcosystemDesign(
            ecosystem_positioning="整合线上线下流量入口",
            key_partners_to_engage=["品牌供应商", "物流配送"],
            orchestration_strategy="以消费者数据平台为底座",
            platform_effect="更多消费者吸引更多品牌",
        ),
        opc=OPCDesign(
            operations_excellence="建立统一运营体系",
            platform_capability="沉淀平台能力",
            content_and_community="构建内容与社群闭环",
            data_flywheel_effect=_long_text("数据飞轮"),
        ),
        three_stage_strategy=ThreeStageStrategy(
            stage_1=ThreeStageStrategyStage(
                title="阶段 1",
                focus="快速验证",
                objective="先完成单点试点验证。",
            ),
            stage_2=ThreeStageStrategyStage(
                title="阶段 2",
                focus="规模扩展",
                objective="再扩展到更多业务单元。",
            ),
            stage_3=ThreeStageStrategyStage(
                title="阶段 3",
                focus="壁垒构建",
                objective="最终沉淀为长期平台能力。",
            ),
            key_risks=["协同不足"],
        ),
        strategic_paths=[
            StrategicPath(
                path_name="稳健试点路径",
                path_type="保守",
                execution_rhythm="以试点验证为先，成熟后再复制扩展",
                key_milestones=["完成试点准备"],
                capability_requirements="优先复用现有团队与客户经营机制",
                expected_outcomes="形成可复制的私域运营能力",
                major_risks=["数据基础薄弱"],
                recommendation_level="推荐",
            )
        ],
        overall_narrative=_long_text("终局总体判断"),
    )


def test_report_builder_does_not_emit_ellipsis_or_removed_labels() -> None:
    """确认报告生成结果中不再保留省略号、整体评分和待补充信息标签。"""
    builder = ReportBuilder()
    report = builder.build(
        assessment=_build_assessment(),
        profile=_build_profile(),
        canvas_diagnosis=_build_canvas(),
        scenario_recommendation=_build_scenarios(),
        case_recommendation=None,
        breakthrough_keys=["customer_relationships"],
        direction_labels=["知识沉淀复用"],
        competitiveness_result=_build_competitiveness(),
        endgame_result=_build_endgame(),
    )

    payload = report.model_dump_json()

    assert "..." not in payload
    assert "…" not in payload
    assert "整体评分" not in payload
    assert "待补充信息" not in payload
    assert "投资需求" not in payload
    assert "时间范围" not in payload
