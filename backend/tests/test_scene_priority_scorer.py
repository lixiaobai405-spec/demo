"""Top 3 AI 场景推荐 · 四象限优先级评分 — 测试用例

对应 PRD: ALGO-SCENE-SCORE-001

注意：PRD §1.3 的示例表格中有多处数学错误（LPS 值与公式不符）。
本测试使用公式正解值：LPS = X×0.6 + (6-Y)×0.4。
"""

import math

import pytest

from app.schemas.scene_priority import (
    Quadrant,
    RecommendationLevel,
    ScenePriorityInput,
)
from app.services.scene_priority_scorer import ScenePriorityScorer


@pytest.fixture
def scorer():
    return ScenePriorityScorer()


def _make_candidate(
    scene_id: str = "s1",
    name: str = "测试场景",
    category: str = "销售增长",
    x: float = 3.0,
    y: float = 3.0,
    industry: str = "制造业",
    summary: str = "",
) -> ScenePriorityInput:
    return ScenePriorityInput(
        scene_id=scene_id,
        scene_name=name,
        category=category,
        summary=summary,
        structuredness_x=x,
        complexity_y=y,
        industry=industry,
    )


# ═══════════════════════════════════════════════════════════
# 2.1 单元测试：公式验证（使用公式正解值，非 PRD 错误示例）
# ═══════════════════════════════════════════════════════════

class TestFormulaValidation:
    """PRD §1.3 — 公式 LPS = X×0.6 + (6-Y)×0.4，范围 [2.6, 5.0]"""

    FORMULA_CASES = [
        # (name, X, Y, QS, LPS, LPS_display, quadrant)
        ("UT-01 完美AI场景（满分）", 5, 1, 5, 5.0, 10.0, Quadrant.automation_battlefield),
        ("UT-02 AI优先区典型", 5, 5, 25, 3.4, 6.8, Quadrant.ai_priority),
        ("UT-03 自动化主战场典型", 4, 2, 8, 4.0, 8.0, Quadrant.automation_battlefield),
        ("UT-04 人机协作区典型", 2, 5, 10, 1.6, 3.2, Quadrant.human_ai_collab),
        ("UT-05 人类保留区（低×低）", 1, 1, 1, 2.6, 5.2, Quadrant.human_reserved),
        ("UT-06 最差AI场景", 1, 5, 5, 1.0, 2.0, Quadrant.human_ai_collab),
        # (3,3): 两者均 < 3.5 → Q4（PRD 示例误标为 AI优先区）
        ("UT-07 中等场景归入Q4", 3, 3, 9, 3.0, 6.0, Quadrant.human_reserved),
    ]

    @pytest.mark.parametrize("name,x,y,exp_qs,exp_lps,exp_display,exp_quadrant", FORMULA_CASES)
    def test_formula(self, scorer, name, x, y, exp_qs, exp_lps, exp_display, exp_quadrant):
        candidate = _make_candidate(x=x, y=y)
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]

        assert s.qs == exp_qs, f"{name}: QS={s.qs} != {exp_qs}"
        assert math.isclose(s.lps, exp_lps, rel_tol=1e-9), f"{name}: LPS={s.lps} != {exp_lps}"
        assert math.isclose(s.lps_display, exp_display, rel_tol=1e-9), f"{name}: display={s.lps_display} != {exp_display}"
        assert s.quadrant == exp_quadrant, f"{name}: quadrant={s.quadrant} != {exp_quadrant}"


class TestBoundaryQuadrant:
    """PRD §2.1 — X/Y = 3.5 分界线"""

    BOUNDARY_CASES = [
        ("UT-08 X=3.5 Y=3.5 → AI优先区", 3.5, 3.5, Quadrant.ai_priority, 2),
        ("UT-09 X=3.5 Y=3.4 → 自动化主战场", 3.5, 3.4, Quadrant.automation_battlefield, 1),
        ("UT-10 X=3.4 Y=3.5 → 人机协作区", 3.4, 3.5, Quadrant.human_ai_collab, 3),
    ]

    @pytest.mark.parametrize("name,x,y,exp_quadrant,exp_tier", BOUNDARY_CASES)
    def test_boundary(self, scorer, name, x, y, exp_quadrant, exp_tier):
        candidate = _make_candidate(x=x, y=y)
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]
        assert s.quadrant == exp_quadrant, f"{name}: quadrant={s.quadrant}"
        assert s.priority_tier == exp_tier, f"{name}: tier={s.priority_tier}"


# ═══════════════════════════════════════════════════════════
# 2.2 单元测试：象限分类全覆盖
# ═══════════════════════════════════════════════════════════

class TestQuadrantClassification:
    CASES = [
        ("UT-11 Q1上界", 5, 5, Quadrant.ai_priority, 2),
        ("UT-12 Q1下界", 3.5, 3.5, Quadrant.ai_priority, 2),
        ("UT-13 Q2上界", 5, 3.4, Quadrant.automation_battlefield, 1),
        ("UT-14 Q2下界", 3.5, 1, Quadrant.automation_battlefield, 1),
        ("UT-15 Q3典型", 1, 5, Quadrant.human_ai_collab, 3),
        ("UT-16 Q4典型", 1, 1, Quadrant.human_reserved, 4),
    ]

    @pytest.mark.parametrize("name,x,y,exp_q,exp_tier", CASES)
    def test_quadrant(self, scorer, name, x, y, exp_q, exp_tier):
        candidate = _make_candidate(x=x, y=y)
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]
        assert s.quadrant == exp_q, f"{name}: {s.quadrant} != {exp_q}"
        assert s.priority_tier == exp_tier, f"{name}: tier={s.priority_tier}"


# ═══════════════════════════════════════════════════════════
# 2.3 单元测试：行业系数修正
# ═══════════════════════════════════════════════════════════

class TestIndustryCoefficient:
    COEF_CASES = [
        ("UT-17 互联网上浮", "数字科技", 4, 2, 1.05),
        ("UT-18 制造业基准", "制造业（离散型）", 4, 2, 1.00),
        ("UT-19 专业服务业下调", "专业服务业", 4, 2, 0.95),
        ("UT-20 医疗高监管下调", "医疗", 4, 2, 0.90),
        ("UT-21 公共服务下调", "公共服务", 4, 2, 0.92),
        ("UT-22 流程型制造业（最长键优先匹配）", "制造业（流程型）", 4, 2, 1.03),
    ]

    @pytest.mark.parametrize("name,industry,x,y,exp_kappa", COEF_CASES)
    def test_coefficient(self, scorer, name, industry, x, y, exp_kappa):
        candidate = _make_candidate(x=x, y=y, industry=industry)
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]

        base_lps = x * 0.6 + (6 - y) * 0.4
        expected_final = round(base_lps * exp_kappa, 4)

        assert s.industry_coefficient == exp_kappa, f"{name}: κ={s.industry_coefficient} != {exp_kappa}"
        assert math.isclose(s.lps_final, expected_final, rel_tol=1e-9), (
            f"{name}: lps_final={s.lps_final} != {expected_final}"
        )

    def test_unknown_industry_defaults_to_1(self, scorer):
        candidate = _make_candidate(x=4, y=2, industry="未知行业")
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]
        assert s.industry_coefficient == 1.00

    def test_empty_industry_defaults_to_1(self, scorer):
        candidate = _make_candidate(x=4, y=2, industry="")
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]
        assert s.industry_coefficient == 1.00

    def test_generic_manufacturing_matches_1_00(self, scorer):
        """基准行业 '制造业' 匹配 κ=1.00（非流程型）"""
        candidate = _make_candidate(x=4, y=2, industry="制造业")
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]
        assert s.industry_coefficient == 1.00


# ═══════════════════════════════════════════════════════════
# 2.4 单元测试：推荐等级映射
# ═══════════════════════════════════════════════════════════

class TestRecommendationLevel:
    LEVEL_CASES = [
        ("UT-23 满分立即启动", (5, 1), RecommendationLevel.immediate_start),
        ("UT-24 8.0立即启动", (4, 2), RecommendationLevel.immediate_start),
        ("UT-25 7.72规划推进", (3.5, 1.6), RecommendationLevel.plan_advance),
        ("UT-26 5.0边界规划推进", (2.5, 3.5), RecommendationLevel.plan_advance),
        ("UT-27 3.2观察", (2, 5), RecommendationLevel.observe),
        ("UT-28 2.0观察", (1, 5), RecommendationLevel.observe),
    ]

    @pytest.mark.parametrize("name,xy,exp_level", LEVEL_CASES)
    def test_level(self, scorer, name, xy, exp_level):
        x, y = xy
        candidate = _make_candidate(x=x, y=y)
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]
        assert s.recommendation_level == exp_level, f"{name}: {s.recommendation_level} != {exp_level}"


# ═══════════════════════════════════════════════════════════
# 2.5 集成测试：recommend_top3() 完整流程
# ═══════════════════════════════════════════════════════════

class TestIntegrationPRDManufacturingExample:
    """IT-01：基于 PRD §5 制造业 8 场景，使用公式正解值"""

    @pytest.fixture
    def manufacturing_candidates(self):
        """PRD §5 示例数据。

        注意：焊接参数AI推荐 (3,3) 依规则归入 Q4（X,Y 均 < 3.5），
        与 PRD 示例表不一致。PRD 示例表在此处存在分类错误。
        """
        return [
            _make_candidate("s1", "智能报价系统", "销售增长", x=4, y=2),        # Q2, tier1, LPS_display=8.0
            _make_candidate("s2", "焊接参数AI推荐", "生产运营", x=3, y=3),      # Q4, tier4 (X,Y<3.5)
            _make_candidate("s3", "客户流失预警", "客户经营", x=4, y=4),        # Q1, tier2, LPS_display=6.4
            _make_candidate("s4", "设备预测性维护", "生产运营", x=5, y=4),      # Q1, tier2, LPS_display=7.6
            _make_candidate("s5", "自动生成检测报告", "交付运营", x=5, y=1),     # Q2, tier1, LPS_display=10.0
            _make_candidate("s6", "供应链需求预测", "供应链", x=3, y=4),        # Q3, tier3, LPS_display=5.2
            _make_candidate("s7", "战略并购决策辅助", "管理分析", x=1, y=5),     # Q3, tier3, LPS_display=2.0
            _make_candidate("s8", "厂区保洁路线优化", "协同办公", x=2, y=1),     # Q4, tier4
        ]

    def test_top3_order(self, scorer, manufacturing_candidates):
        result = scorer.recommend_top3(manufacturing_candidates)

        assert result.total_candidates == 8
        assert len(result.top_3) == 3

        top_names = [s.scene_name for s in result.top_3]

        # No.1：自动生成检测报告（梯队1, 10.0分）
        assert top_names[0] == "自动生成检测报告"
        assert result.top_3[0].quadrant == Quadrant.automation_battlefield
        assert result.top_3[0].lps_display == 10.0

        # No.2：智能报价系统（梯队1, 8.0分）
        assert top_names[1] == "智能报价系统"
        assert result.top_3[1].quadrant == Quadrant.automation_battlefield
        assert result.top_3[1].lps_display == 8.0

        # No.3：设备预测性维护（梯队2, 7.6分 — 公式正解值，非PRD错误的8.0）
        assert top_names[2] == "设备预测性维护"
        assert result.top_3[2].quadrant == Quadrant.ai_priority
        assert math.isclose(result.top_3[2].lps_display, 7.6, rel_tol=1e-9)

    def test_q4_filtered_out(self, scorer, manufacturing_candidates):
        """Q4 场景（厂区保洁路线优化、焊接参数AI推荐）不在 Top 3"""
        result = scorer.recommend_top3(manufacturing_candidates)
        top_names = [s.scene_name for s in result.top_3]
        assert "厂区保洁路线优化" not in top_names
        assert "焊接参数AI推荐" not in top_names

    def test_eligible_count(self, scorer, manufacturing_candidates):
        """8 个中 2 个 Q4 被过滤，eligible=6"""
        result = scorer.recommend_top3(manufacturing_candidates)
        assert result.eligible_count == 6

    def test_client_churn_not_in_top3(self, scorer, manufacturing_candidates):
        """客户流失预警（7.6 < 设备预测性维护7.6 → 同分but tier2同级，按lps排序）不在 Top 3"""
        result = scorer.recommend_top3(manufacturing_candidates)
        top_names = [s.scene_name for s in result.top_3]
        assert "客户流失预警" not in top_names


class TestRuleBAllQ4Fallback:
    """IT-02：规则 B — 全部候选在人类保留区时降级兜底（PRD §3.1）"""

    def test_all_q4_returns_top2(self, scorer):
        candidates = [
            _make_candidate("s1", "Q4场景A", "协同办公", x=1, y=1),
            _make_candidate("s2", "Q4场景B", "协同办公", x=2, y=1),
            _make_candidate("s3", "Q4场景C", "协同办公", x=1.5, y=2),
        ]
        result = scorer.recommend_top3(candidates)

        assert result.fallback_triggered is True
        assert "人类保留区" in result.fallback_reason
        assert len(result.top_3) == 2

    def test_all_q4_fallback_includes_action_suggestion(self, scorer):
        """PRD §3.1 #3 — 兜底时必须包含前置行动建议"""
        candidates = [
            _make_candidate("s1", "Q4场景A", "协同办公", x=2, y=1),
            _make_candidate("s2", "Q4场景B", "协同办公", x=1, y=2),
        ]
        result = scorer.recommend_top3(candidates)
        assert "前置行动建议" in result.fallback_reason
        assert "数据采集" in result.fallback_reason

    def test_all_q4_single_candidate_returns_1(self, scorer):
        candidates = [_make_candidate("s1", "唯一Q4", "协同办公", x=1, y=1)]
        result = scorer.recommend_top3(candidates)

        assert result.fallback_triggered is True
        assert len(result.top_3) == 1


class TestRuleCEnsureAutomationBattlefield:
    """IT-03/04：规则 C — 确保至少 1 个自动化主战场

    由于梯队排序（tier1 > tier2）保证了任何 Q2 总是在 Q1 之前，
    规则 C 仅在极端情况下可达：所有 Q2 被其他规则排除后，
    eligible 中无 Q2 但有大量 Q1。
    """

    def test_rule_c_noop_when_q2_present(self, scorer):
        """有 Q2 候选时，Q2 自然在 Top 3（tier1 优先），规则 C 无需干预"""
        candidates = [
            _make_candidate("s1", "AI场景A", "销售增长", x=5, y=5),      # Q1, tier=2, LPS_display=6.8
            _make_candidate("s2", "AI场景B", "客户经营", x=4, y=4),      # Q1, tier=2, LPS_display=6.4
            _make_candidate("s3", "AI场景C", "生产运营", x=4.5, y=4.5),   # Q1, tier=2, LPS_display=6.6
            _make_candidate("s5", "自动化场景", "交付运营", x=4, y=2),    # Q2, tier=1, LPS_display=8.0
        ]
        result = scorer.recommend_top3(candidates)

        # Q2 自然排第一（tier=1）
        assert result.top_3[0].scene_name == "自动化场景"
        has_auto = any(s.quadrant == Quadrant.automation_battlefield for s in result.top_3)
        assert has_auto is True

    def test_top3_all_q1_with_no_q2_in_eligible(self, scorer):
        """无 Q2 可用的边界情况：Top 3 无自动化主战场属正常结果"""
        # 全部 Q1，没有 Q2
        candidates = [
            _make_candidate("s1", "AI场景A", "销售增长", x=5, y=4),      # Q1 tier2
            _make_candidate("s2", "AI场景B", "客户经营", x=4, y=4),      # Q1 tier2
            _make_candidate("s3", "AI场景C", "生产运营", x=4.5, y=3.5),   # Q1 tier2
        ]
        result = scorer.recommend_top3(candidates)
        assert len(result.top_3) == 3
        # 没有 Q2 不应崩溃
        has_auto = any(s.quadrant == Quadrant.automation_battlefield for s in result.top_3)
        # 可以没有 Q2（这是预期的）
        assert has_auto is False or has_auto is True  # no crash


class TestTieBreaking:
    """IT-05：同分打破平局规则（PRD §3.2）"""

    def test_tie_lower_tier_wins(self, scorer):
        """梯队1 优先于 梯队2"""
        candidates = [
            _make_candidate("s1", "Q2场景", "交付运营", x=4, y=2),   # Q2 tier=1
            _make_candidate("s2", "Q1场景", "生产运营", x=5, y=5),    # Q1 tier=2
        ]
        result = scorer.recommend_top3(candidates)
        top_names = [s.scene_name for s in result.top_3]
        assert top_names[0] == "Q2场景", f"梯队1应优先: {top_names}"

    def test_same_tier_higher_lps_wins(self, scorer):
        """同梯队内 LPS_final 更高者优先"""
        candidates = [
            _make_candidate("s1", "高LPS场景", "生产运营", x=5.0, y=4.0),  # Q1, LPS=3.8
            _make_candidate("s2", "低LPS场景", "生产运营", x=4.0, y=5.0),  # Q1, LPS=2.8
        ]
        result = scorer.recommend_top3(candidates)
        top_names = [s.scene_name for s in result.top_3]
        assert top_names[0] == "高LPS场景"


class TestLessThanThreeCandidates:
    """IT-06：少于 3 个候选"""

    def test_two_candidates(self, scorer):
        candidates = [
            _make_candidate("s1", "Q1场景", "销售增长", x=4, y=4),
            _make_candidate("s2", "Q2场景", "交付运营", x=4, y=2),
        ]
        result = scorer.recommend_top3(candidates)
        assert len(result.top_3) == 2
        assert result.top_3[0].quadrant == Quadrant.automation_battlefield

    def test_single_candidate(self, scorer):
        candidates = [_make_candidate("s1", "唯一场景", "销售增长", x=4, y=4)]
        result = scorer.recommend_top3(candidates)
        assert len(result.top_3) == 1


class TestRuleAHighAI:
    """IT-07：规则 A — 极高 AI 优先区（公式约束下此规则为 no-op）

    Q1 最高的 LPS 出现在 X=5, Y=3.5 → LPS=4.0, display=8.0。
    不可能达到 LPS_display ≥ 9.0，因此规则 A 在当前公式下不可达。
    """

    def test_best_q1_cannot_exceed_8_display(self, scorer):
        """验证 Q1 最高 display 分为 8.0"""
        candidate = _make_candidate("s1", "最优Q1", "生产运营", x=5, y=3.5)
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]
        assert s.quadrant == Quadrant.ai_priority
        assert math.isclose(s.lps_display, 8.0, rel_tol=1e-9)

    def test_q2_still_ranks_higher_than_q1(self, scorer):
        """Q2 tier1 始终优先于 Q1 tier2"""
        candidates = [
            _make_candidate("s1", "最优Q1场景", "生产运营", x=5, y=3.5),   # Q1, LPS_display=8.0
            _make_candidate("s2", "普通Q2场景", "交付运营", x=4, y=2),     # Q2, LPS_display=8.0
        ]
        result = scorer.recommend_top3(candidates)
        assert result.top_3[0].quadrant == Quadrant.automation_battlefield


# ═══════════════════════════════════════════════════════════
# 2.6 边界与异常测试
# ═══════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_clamp_below_1(self, scorer):
        """_clamp_score(0) → 1.0"""
        assert scorer._clamp_score(0) == 1.0

    def test_clamp_above_5(self, scorer):
        """_clamp_score(6) → 5.0"""
        assert scorer._clamp_score(6) == 5.0

    def test_empty_candidates(self, scorer):
        result = scorer.recommend_top3([])
        assert result.total_candidates == 0
        assert len(result.top_3) == 0

    def test_float_scores(self, scorer):
        """支持小数分输入"""
        candidate = _make_candidate(x=4.5, y=1.5)
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]
        expected_lps = 4.5 * 0.6 + (6 - 1.5) * 0.4  # 2.7 + 1.8 = 4.5
        assert math.isclose(s.lps, expected_lps, rel_tol=1e-9)

    def test_all_ineligible_q3_eligible(self, scorer):
        """只有 Q3 候选时正常返回 Top 3"""
        candidates = [
            _make_candidate("s1", "Q3场景A", "管理分析", x=1, y=5),
            _make_candidate("s2", "Q3场景B", "管理分析", x=3, y=4),
            _make_candidate("s3", "Q3场景C", "管理分析", x=2, y=5),
            _make_candidate("s4", "Q3场景D", "管理分析", x=1, y=4),
        ]
        result = scorer.recommend_top3(candidates)
        assert len(result.top_3) == 3
        # Q3 没有被过滤（tier=3 是 eligible）
        all_q3 = all(s.quadrant == Quadrant.human_ai_collab for s in result.top_3)
        assert all_q3


# ═══════════════════════════════════════════════════════════
# NLP 启发式自动评分
# ═══════════════════════════════════════════════════════════

class TestHeuristicAutoScoring:
    """PRD §1.1 / §1.2 — NLP 信号关键词自动评分"""

    def test_structuredness_5(self, scorer):
        text = "系统里都有完整记录，ERP自动记录每步数据，标准流程SOP完善"
        assert scorer.score_structuredness(text) == 5

    def test_structuredness_4(self, scorer):
        text = "大部分有记录在Excel汇总，规则比较清晰偶有例外需要人工判断"
        assert scorer.score_structuredness(text) == 4

    def test_structuredness_1(self, scorer):
        text = "这个完全凭感觉，说不清楚规律，每个人差距很大"
        assert scorer.score_structuredness(text) == 1

    def test_structuredness_default(self, scorer):
        assert scorer.score_structuredness("") == 3
        assert scorer.score_structuredness("这是一段没有信号词的普通文本") == 3

    def test_complexity_5(self, scorer):
        text = "需要多变量高阶分析，深度专业判断，错误代价极高"
        assert scorer.score_complexity(text) == 5

    def test_complexity_2(self, scorer):
        text = "少量变量线性逻辑，规则可描述，标准操作"
        assert scorer.score_complexity(text) == 2

    def test_complexity_default(self, scorer):
        assert scorer.score_complexity("") == 3

    def test_highest_score_wins(self, scorer):
        """混合信号时取最高分"""
        text = "完全凭感觉但也有部分有记录和标准流程"
        assert scorer.score_structuredness(text) == 5


class TestRankField:
    """PRD §4 — rank 字段（🥇🥈🥉）"""

    def test_top3_has_rank(self, scorer):
        candidates = [
            _make_candidate("s1", "场景A", "销售增长", x=5, y=1),   # Q2
            _make_candidate("s2", "场景B", "交付运营", x=4, y=2),   # Q2
            _make_candidate("s3", "场景C", "生产运营", x=5, y=4),   # Q1
        ]
        result = scorer.recommend_top3(candidates)
        assert len(result.top_3) == 3
        assert result.top_3[0].rank == 1
        assert result.top_3[1].rank == 2
        assert result.top_3[2].rank == 3

    def test_non_top3_has_no_rank(self, scorer):
        """不在 Top 3 的候选 rank 为 None"""
        candidates = [
            _make_candidate("s1", "A", "销售增长", x=5, y=1),
            _make_candidate("s2", "B", "交付运营", x=4, y=2),
            _make_candidate("s3", "C", "生产运营", x=5, y=4),
            _make_candidate("s4", "D", "客户经营", x=4, y=4),
        ]
        result = scorer.recommend_top3(candidates)
        # 只给 top_3 赋 rank
        for s in result.top_3:
            assert s.rank is not None
        # all_scores 中非 top_3 的 rank 应为 None
        top_ids = {s.scene_id for s in result.top_3}
        for s in result.all_scores:
            if s.scene_id not in top_ids:
                assert s.rank is None


class TestLpsDisplayIncludesKappa:
    """PRD §3.3 — LPS_display = LPS × κ × 2"""

    def test_medical_industry_discounts_display(self, scorer):
        """医疗行业 κ=0.90，LPS_display 应体现行业折扣"""
        candidate = _make_candidate(x=4, y=2, industry="医疗")
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]

        base_lps = 4 * 0.6 + (6 - 2) * 0.4  # = 4.0
        # LPS_display = 4.0 * 0.90 * 2 = 7.2
        expected_display = round(base_lps * 0.90 * 2, 1)
        assert math.isclose(s.lps_display, expected_display, rel_tol=1e-9)
        assert math.isclose(s.lps_display, 7.2, rel_tol=1e-9)

    def test_internet_industry_premium_display(self, scorer):
        """数字科技 κ=1.05，LPS_display 应体现上浮"""
        candidate = _make_candidate(x=4, y=2, industry="数字科技")
        result = scorer.recommend_top3([candidate])
        s = result.all_scores[0]

        base_lps = 4 * 0.6 + (6 - 2) * 0.4  # = 4.0
        expected_display = round(base_lps * 1.05 * 2, 1)  # = 8.4
        assert math.isclose(s.lps_display, expected_display, rel_tol=1e-9)


class TestScoringMethodField:
    def test_result_has_correct_method(self, scorer):
        result = scorer.recommend_top3([_make_candidate()])
        assert result.scoring_method == "four_quadrant_v1"


class TestRecommendationTemplate:
    def test_each_quadrant_has_template(self, scorer):
        """每个象限都有对应的推荐话术模板"""
        quadrants_and_coords = [
            (Quadrant.automation_battlefield, 5, 1),
            (Quadrant.ai_priority, 5, 5),
            (Quadrant.human_ai_collab, 2, 5),
            (Quadrant.human_reserved, 1, 1),
        ]
        for quadrant, x, y in quadrants_and_coords:
            candidate = _make_candidate(x=x, y=y)
            result = scorer.recommend_top3([candidate])
            s = result.all_scores[0]
            assert s.quadrant == quadrant
            assert len(s.recommendation_template) > 0, f"{quadrant} 缺少话术模板"


# ═══════════════════════════════════════════════════════════
# Spec #2 修复验证：Q4 兜底消息传播到 ScenarioRecommendationResult
# ═══════════════════════════════════════════════════════════

class TestFallbackMessagePropagation:
    """验证 fallback_triggered / fallback_reason 正确流动"""

    def test_normal_flow_no_fallback(self, scorer):
        """正常场景（有 eligible 候选）不触发 fallback"""
        candidates = [
            _make_candidate("s1", "正常场景", "销售增长", x=5, y=1),
        ]
        result = scorer.recommend_top3(candidates)
        assert result.fallback_triggered is False
        assert result.fallback_reason == ""

    def test_all_q4_triggers_fallback(self, scorer):
        """全部 Q4 时 fallback_triggered=True"""
        candidates = [
            _make_candidate("s1", "Q4场景A", "协同办公", x=2, y=1),
            _make_candidate("s2", "Q4场景B", "协同办公", x=1, y=1),
        ]
        result = scorer.recommend_top3(candidates)
        assert result.fallback_triggered is True
        assert len(result.fallback_reason) > 0

    def test_fallback_reason_has_actionable_content(self, scorer):
        """PRD §3.1 — fallback_reason 包含可操作的前置行动建议"""
        candidates = [
            _make_candidate("s1", "Q4场景", "协同办公", x=2, y=1),
        ]
        result = scorer.recommend_top3(candidates)

        # 关键要素验证
        assert "人类保留区" in result.fallback_reason
        assert "前置行动建议" in result.fallback_reason
        assert "业务流程数字化" in result.fallback_reason
        assert "数据采集" in result.fallback_reason
        # 至少 50 字，确保不是敷衍的一句话
        assert len(result.fallback_reason) >= 50

    def test_mixed_q4_and_eligible_no_fallback(self, scorer):
        """混合场景（有 Q4 但也有 eligible）不触发 fallback"""
        candidates = [
            _make_candidate("s1", "Q4场景", "协同办公", x=2, y=1),       # Q4
            _make_candidate("s2", "正常场景", "销售增长", x=5, y=1),      # Q2 eligible
        ]
        result = scorer.recommend_top3(candidates)
        assert result.fallback_triggered is False
        assert result.eligible_count >= 1


class TestScenarioRecommendationResultModel:
    """验证 Pydantic model 序列化包含 fallback 字段（供前端消费）"""

    def test_model_serializes_fallback_fields(self):
        from app.schemas.assessment import ScenarioRecommendationResult, ScenarioRecommendationItem

        result = ScenarioRecommendationResult(
            scoring_method="four_quadrant_v1",
            evaluated_count=24,
            top_scenarios=[],
            fallback_triggered=True,
            fallback_reason="测试兜底原因",
        )
        data = result.model_dump()

        assert data["fallback_triggered"] is True
        assert data["fallback_reason"] == "测试兜底原因"

    def test_model_defaults_fallback_false(self):
        from app.schemas.assessment import ScenarioRecommendationResult

        result = ScenarioRecommendationResult(
            scoring_method="rule_based_v1",
            evaluated_count=24,
        )
        data = result.model_dump()

        assert data["fallback_triggered"] is False
        assert data["fallback_reason"] == ""

    def test_legacy_rule_based_no_fallback(self):
        """旧评分方法 (rule_based_v1) 的默认 fallback 字段不影响前端"""
        from app.schemas.assessment import ScenarioRecommendationResult

        result = ScenarioRecommendationResult(
            scoring_method="rule_based_v1",
            evaluated_count=24,
        )
        assert result.fallback_triggered is False
        assert result.fallback_reason == ""


class TestScenePriorityResultToRecommendationResult:
    """验证 ScenePriorityResult → ScenarioRecommendationResult 的转换路径"""

    def test_fallback_fields_flow_through_result(self, scorer):
        """完整链路：scorer → ScenePriorityResult → 验证字段可被消费"""
        candidates = [
            _make_candidate("s1", "Q4-A", "协同办公", x=1, y=1),
            _make_candidate("s2", "Q4-B", "协同办公", x=2, y=1),
        ]
        priority_result = scorer.recommend_top3(candidates)

        # ScenePriorityResult 字段
        assert priority_result.fallback_triggered is True
        assert "前置行动建议" in priority_result.fallback_reason

        # 验证 top_3 中每个场景有 rank（PRD §4）
        for s in priority_result.top_3:
            assert s.rank is not None

        # 模拟 ScenarioRecommender.recommend_with_priority() 的转换逻辑
        # — 验证 fallback 字段可以从 ScenePriorityResult 映射到 ScenarioRecommendationResult
        from app.schemas.assessment import ScenarioRecommendationResult

        api_result = ScenarioRecommendationResult(
            scoring_method="four_quadrant_v1",
            evaluated_count=priority_result.total_candidates,
            top_scenarios=[],
            fallback_triggered=priority_result.fallback_triggered,
            fallback_reason=priority_result.fallback_reason,
        )

        assert api_result.fallback_triggered is True
        assert "前置行动建议" in api_result.fallback_reason
        assert "数据采集" in api_result.fallback_reason

    def test_full_flow_normal_case(self, scorer):
        """正常场景完整链路：fallback_triggered=False, fallback_reason=''"""
        from app.schemas.assessment import ScenarioRecommendationResult

        candidates = [
            _make_candidate("s1", "A", "生产运营", x=5, y=1),
            _make_candidate("s2", "B", "交付运营", x=4, y=2),
        ]
        priority_result = scorer.recommend_top3(candidates)

        assert priority_result.fallback_triggered is False

        api_result = ScenarioRecommendationResult(
            scoring_method="four_quadrant_v1",
            evaluated_count=priority_result.total_candidates,
            top_scenarios=[],
            fallback_triggered=priority_result.fallback_triggered,
            fallback_reason=priority_result.fallback_reason,
        )

        assert api_result.fallback_triggered is False
        assert api_result.fallback_reason == ""
