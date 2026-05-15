from pathlib import Path
import json
import sys
from types import SimpleNamespace

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.api.routes.assessments import _build_endgame_result_from_record
from app.schemas.assessment import (
    BusinessModelCanvasResult,
    CanvasBlockResult,
    CanvasDiagnosisResult,
)
from app.schemas.competitiveness import (
    CompetitivenessResult,
    CoreAdvantage,
    DeliveryStrategy,
    PointToLineConnection,
    VPReconstruction,
)
from app.schemas.direction import DirectionSuggestion
from app.services.endgame_analyzer import EndgameAnalyzer


def _build_canvas() -> CanvasDiagnosisResult:
    """构造终局分析所需的最小画布诊断数据。"""
    return CanvasDiagnosisResult(
        generation_mode="mock",
        overall_score=76,
        weakest_blocks=["客户关系", "渠道通路"],
        recommended_focus=["聚焦客户关系", "完善渠道协同"],
        canvas=BusinessModelCanvasResult(
            overall_summary="整体画布具备推进条件。",
            blocks=[
                CanvasBlockResult(
                    key="customer_relationships",
                    title="客户关系",
                    current_state="客户关系仍以人工维护为主。",
                    diagnosis="缺少统一的客户经营机制。",
                    ai_opportunity="可引入 AI 做客户分层和触达编排。",
                    missing_information="内部字段，仅用于算法判断。",
                )
            ],
        ),
    )


def _build_competitiveness() -> CompetitivenessResult:
    """构造带有三阶段推进策略的竞争力分析结果。"""
    return CompetitivenessResult(
        generation_mode="rule_based",
        vp_reconstruction=VPReconstruction(
            current_vp="帮助门店提升经营效率",
            enhanced_vp="通过客户经营和知识复用形成差异化竞争力",
            differentiation_points=["客户经营深化", "知识资产复用"],
            customer_value_shift="从单点提效升级为持续经营。",
        ),
        connections=[
            PointToLineConnection(
                line_name="客户关系深化线",
                point_ids=["direction-1"],
                point_titles=["客户分层经营"],
                strategic_narrative="围绕客户关系深化形成系统性能力。",
                competitive_impact="提高复购与留存",
                key_metrics=["复购率"],
            )
        ],
        advantages=[
            CoreAdvantage(
                advantage_name="客户经营优势",
                source_elements=["客户关系"],
                description="形成更强的客户经营闭环。",
                barrier_level="高",
            )
        ],
        delivery_strategy=DeliveryStrategy(
            phase_1_quick_win="先用单一门店试点验证客户分层与触达闭环。",
            phase_2_scale="将试点扩展到区域门店，并建立统一运营机制。",
            phase_3_moat="把沉淀下来的运营机制平台化为长期壁垒。",
            key_risks=["跨团队协同不足"],
        ),
        overall_narrative="竞争力已具备向终局迁移的基础。",
    )


def _build_selected_directions() -> list[DirectionSuggestion]:
    """构造终局分析引用的方向选择结果。"""
    return [
        DirectionSuggestion(
            direction_id="direction-1",
            element_key="customer_relationships",
            title="客户分层经营",
            description="围绕客户分层做精细化经营。",
            expected_impact="提升复购率",
            data_needed=["会员数据"],
            related_scenario_categories=["客户服务"],
        )
    ]


def test_endgame_analyzer_moves_three_stage_strategy_into_endgame_result() -> None:
    """确认终局分析结果承接三阶段推进策略，而不是继续留在竞争力页独占。"""
    analyzer = EndgameAnalyzer()

    result = analyzer.analyze(
        industry="零售",
        canvas_diagnosis=_build_canvas(),
        breakthrough_keys=["customer_relationships", "channels"],
        selected_directions=_build_selected_directions(),
        competitiveness_result=_build_competitiveness(),
    )

    assert result.three_stage_strategy.stage_1.title == "阶段 1"
    assert result.three_stage_strategy.stage_1.focus == "快速验证"
    assert result.three_stage_strategy.stage_1.objective == "先用单一门店试点验证客户分层与触达闭环。"
    assert len(result.three_stage_strategy.stage_1.key_actions) > 0
    assert len(result.three_stage_strategy.stage_1.key_risks) > 0
    assert len(result.three_stage_strategy.stage_1.strategy) > 0
    assert result.three_stage_strategy.stage_2.objective == "将试点扩展到区域门店，并建立统一运营机制。"
    assert result.three_stage_strategy.stage_3.objective == "把沉淀下来的运营机制平台化为长期壁垒。"
    assert result.three_stage_strategy.key_risks == ["跨团队协同不足"]


def test_endgame_analyzer_uses_qualitative_strategic_paths() -> None:
    """确认终局多路径推演改为定性表达，不再输出月份和预算金额。"""
    analyzer = EndgameAnalyzer()

    result = analyzer.analyze(
        industry="零售",
        canvas_diagnosis=_build_canvas(),
        breakthrough_keys=["customer_relationships", "channels"],
        selected_directions=_build_selected_directions(),
        competitiveness_result=_build_competitiveness(),
    )

    payload = result.model_dump_json()

    assert "Month " not in payload
    assert "个月" not in payload
    assert "预算" not in payload
    assert "万" not in payload
    assert result.strategic_paths[0].execution_rhythm
    assert result.strategic_paths[0].capability_requirements


def test_build_endgame_result_from_record_rehydrates_three_stage_strategy() -> None:
    """确认持久化后的终局结果可以正确还原三阶段推进策略结构。"""
    record = SimpleNamespace(
        generation_mode="rule_based",
        private_domain_json=json.dumps(
            {
                "current_state": "私域基础薄弱",
                "target_model": "建立统一客户经营私域",
                "key_strategies": ["统一客户视图"],
                "customer_retention_loop": "触点数据化 -> 分层运营 -> 价值留存",
                "revenue_impact": "增强留存与复购",
            },
            ensure_ascii=False,
        ),
        ecosystem_json=json.dumps(
            {
                "ecosystem_positioning": "连接品牌与消费者",
                "key_partners_to_engage": ["品牌供应商"],
                "orchestration_strategy": "围绕数据平台做协同",
                "platform_effect": "更多伙伴带来更强协同",
            },
            ensure_ascii=False,
        ),
        opc_json=json.dumps(
            {
                "operations_excellence": "建立统一运营机制",
                "platform_capability": "沉淀平台能力",
                "content_and_community": "建设内容与社群",
                "data_flywheel_effect": "数据沉淀形成正循环",
            },
            ensure_ascii=False,
        ),
        strategic_paths_json=json.dumps(
            [
                {
                    "path_name": "稳健试点路径",
                    "path_type": "保守",
                    "execution_rhythm": "以试点验证为先，成熟后再复制扩展",
                    "key_milestones": ["完成试点准备"],
                    "capability_requirements": "优先复用现有团队与客户经营机制",
                    "expected_outcomes": "形成可复制样板",
                    "major_risks": ["推进节奏不一致"],
                    "recommendation_level": "推荐",
                }
            ],
            ensure_ascii=False,
        ),
        three_stage_strategy_json=json.dumps(
            {
                "stage_1": {
                    "title": "阶段 1",
                    "focus": "快速验证",
                    "objective": "验证单点业务闭环",
                },
                "stage_2": {
                    "title": "阶段 2",
                    "focus": "规模扩展",
                    "objective": "复制到更多业务单元",
                },
                "stage_3": {
                    "title": "阶段 3",
                    "focus": "壁垒构建",
                    "objective": "沉淀为长期平台能力",
                },
                "key_risks": ["组织协同不足"],
            },
            ensure_ascii=False,
        ),
        overall_narrative="终局方向清晰。",
    )

    result = _build_endgame_result_from_record(record)

    assert result.three_stage_strategy.stage_1.objective == "验证单点业务闭环"
    assert result.three_stage_strategy.stage_2.focus == "规模扩展"
    assert result.three_stage_strategy.stage_3.title == "阶段 3"
    assert result.three_stage_strategy.key_risks == ["组织协同不足"]
