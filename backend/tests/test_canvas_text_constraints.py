from app.schemas.assessment import (
    BusinessModelCanvasResult,
    CanvasBlockResult,
)
from app.services.llm_client import normalize_canvas_text_constraints


def test_normalize_canvas_text_constraints_keeps_complete_short_sentences():
    canvas = BusinessModelCanvasResult(
        overall_summary="summary",
        blocks=[
            CanvasBlockResult(
                key="key_activities",
                title="关键活动",
                current_state="当前状态保持原样。",
                diagnosis=(
                    "核心流程缺 SOP，订货依赖店长个人经验，导致网红零食断货或滞销并存。"
                    "跨部门协同效率偏低，影响门店运营复制。"
                ),
                ai_opportunity=(
                    "AI 可优先用于智能订货与库存预测，自动生成补货建议。"
                    "也可以用于会员营销和门店巡检。"
                ),
                missing_information="missing",
            )
        ],
    )

    normalized = normalize_canvas_text_constraints(canvas)
    block = normalized.blocks[0]

    assert block.current_state == "当前状态保持原样。"
    assert block.diagnosis == "核心流程缺 SOP，订货依赖店长个人经验，导致网红零食断货或滞销并存。"
    assert len(block.diagnosis) <= 100
    assert block.ai_opportunity == "AI 可优先用于智能订货与库存预测，自动生成补货建议。"
    assert len(block.ai_opportunity) <= 80


def test_normalize_canvas_text_constraints_avoids_mid_sentence_cutoff_when_possible():
    canvas = BusinessModelCanvasResult(
        overall_summary="summary",
        blocks=[
            CanvasBlockResult(
                key="customer_segments",
                title="客户细分",
                current_state="当前状态保持原样。",
                diagnosis=(
                    "客户画像粗粒度，未按复购频次、客单价、家庭结构和购物偏好形成可运营标签。"
                    "后续还有更多解释。"
                ),
                ai_opportunity=(
                    "基于会员消费数据构建统一客户画像，优先支撑精准选品和个性化触达。"
                    "其他机会暂不展开。"
                ),
                missing_information="missing",
            )
        ],
    )

    normalized = normalize_canvas_text_constraints(canvas)
    block = normalized.blocks[0]

    assert block.diagnosis.endswith("。")
    assert "后续还有更多解释" not in block.diagnosis
    assert block.ai_opportunity.endswith("。")
    assert "其他机会" not in block.ai_opportunity
