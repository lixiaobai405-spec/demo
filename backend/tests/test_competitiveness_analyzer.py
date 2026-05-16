from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.assessment import BusinessModelCanvasResult, CanvasBlockResult, CanvasDiagnosisResult
from app.schemas.direction import DirectionSuggestion
from app.services.competitiveness_analyzer import CompetitivenessAnalyzer


def _build_canvas() -> CanvasDiagnosisResult:
    """构造竞争力分析所需的最小画布数据。"""
    return CanvasDiagnosisResult(
        generation_mode="mock",
        overall_score=80,
        weakest_blocks=["客户关系"],
        recommended_focus=["完善客户关系"],
        canvas=BusinessModelCanvasResult(
            overall_summary="整体画布具备推进条件。",
            blocks=[
                CanvasBlockResult(
                    key="value_propositions",
                    title="价值主张",
                    current_state="帮助客户提升服务效率。",
                    diagnosis="价值主张需要增强。",
                    ai_opportunity="可通过 AI 串联关键环节。",
                    missing_information="内部字段。",
                )
            ],
        ),
    )


def _build_directions() -> list[DirectionSuggestion]:
    """构造可映射到客户响应速度线的方向数据。"""
    return [
        DirectionSuggestion(
            direction_id="direction-1",
            element_key="customer_relationships",
            title="客户健康度评分",
            description="提前识别客户变化。",
            expected_impact="缩短响应周期",
            data_needed=["会员数据"],
            related_scenario_categories=["客户服务"],
        ),
        DirectionSuggestion(
            direction_id="direction-2",
            element_key="key_activities",
            title="人才技能匹配与梯队建设",
            description="提升关键岗位协同。",
            expected_impact="提升服务效率",
            data_needed=["人力数据"],
            related_scenario_categories=["售前效率"],
        ),
    ]


def test_competitiveness_analyzer_builds_single_line_summary() -> None:
    """确认线路卡片生成一句摘要，保留联动逻辑并移除竞争壁垒。"""
    analyzer = CompetitivenessAnalyzer()

    result = analyzer.analyze(
        canvas_diagnosis=_build_canvas(),
        breakthrough_keys=["customer_relationships"],
        selected_directions=_build_directions(),
    )

    customer_line = next(conn for conn in result.connections if conn.line_name == "客户响应速度线")

    assert customer_line.strategic_narrative == (
        "形成从客户洞察到快速响应的协同闭环，"
        "缩短从需求识别到价值交付的周期，提升客户满意度和复购率。"
    )
    assert "提升客户满意度和复购率" in customer_line.strategic_narrative
    assert "将客户健康度评分" not in customer_line.strategic_narrative
    assert "AI不再只是辅助工具" in customer_line.linkage_logic
    assert "客户健康度评分" in customer_line.linkage_logic
    assert customer_line.competitive_moat == ""
