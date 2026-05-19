"""Top 3 AI 场景推荐 · 四象限优先级评分引擎

对应 PRD: ALGO-SCENE-SCORE-001
"""

from __future__ import annotations

from app.schemas.scene_priority import (
    AUTO_REPLACEMENT_TOLERANCE,
    COMPLEXITY_SIGNALS,
    DEFAULT_INDUSTRY_COEFFICIENT,
    IMMEDIATE_START_THRESHOLD,
    INDUSTRY_COEFFICIENTS,
    LPS_DISPLAY_MULTIPLIER,
    PLAN_ADVANCE_THRESHOLD,
    QUADRANT_RECOMMENDATION_TEMPLATES,
    QUADRANT_THRESHOLD,
    STRUCTUREDNESS_SIGNALS,
    WEIGHT_X,
    WEIGHT_Y_INV,
    Y_INVERSION_BASE,
    Quadrant,
    RecommendationLevel,
    ScenePriorityInput,
    ScenePriorityResult,
    ScenePriorityScore,
)


class ScenePriorityScorer:
    """四象限场景优先级评分器。

    算法分两层：
      第一层：QS = X × Y  — 象限定位，不做取反
      第二层：LPS = X×0.6 + (6-Y)×0.4  — 落地优先级，复杂度取反
    """

    # ── 公开 API ────────────────────────────────────────

    def recommend_top3(
        self,
        candidates: list[ScenePriorityInput],
    ) -> ScenePriorityResult:
        """主入口：输入候选场景列表，输出 Top 3 推荐结果。

        实现 PRD §2.2 推荐决策伪代码。
        """
        if not candidates:
            return ScenePriorityResult(
                total_candidates=0,
                eligible_count=0,
            )

        # Step 1：计算每个场景的完整评分
        all_scores = [self._score_one(c) for c in candidates]

        # Step 2：过滤人类保留区（Q4，梯队4）
        eligible = [s for s in all_scores if s.priority_tier <= 3]

        # Step 3：按梯队优先 + 同梯队内 LPS_display 降序 + 打破平局（PRD §3.2）
        eligible.sort(key=self._sort_key)

        fallback_triggered = False
        fallback_reason = ""

        # 规则 B：若全部在人类保留区，降级兜底（PRD §3.1）
        if not eligible:
            fallback_triggered = True
            fallback_reason = (
                "所有候选场景均落入人类保留区，返回LPS最高的前3个作为兜底推荐。"
                "⚠️ 前置行动建议：建议优先进行业务流程数字化改造与数据采集基础建设，"
                "包括建立核心业务数据库、梳理SOP流程、部署数据采集工具等，"
                "以提升场景的结构化程度，为后续AI落地创造条件。"
            )
            all_scores.sort(key=lambda s: -s.lps_display)
            eligible = all_scores[:3]

        # 规则 A：极高 AI 优先区场景可突破梯队（PRD pseudocode L228-231）
        if eligible and eligible[0].quadrant == Quadrant.ai_priority and eligible[0].lps_display >= 9.0:
            pass  # 已足够高，保持原位

        # 确定 Top 3 + 分配排名（不足时从 Q4 补足，兜底时不重复补）
        if len(eligible) < 3 and not fallback_triggered:
            q4_candidates = [s for s in all_scores if s.priority_tier > 3]
            q4_candidates.sort(key=lambda s: -s.lps_display)
            top_3 = list(eligible) + q4_candidates[:3 - len(eligible)]
        elif len(eligible) <= 3:
            top_3 = list(eligible)
        else:
            top_3 = list(eligible[:3])
            # 规则 C：确保至少 1 个自动化主战场（PRD pseudocode L237-249）
            has_auto = any(s.quadrant == Quadrant.automation_battlefield for s in top_3)
            if not has_auto:
                auto_scenes = [
                    s for s in eligible if s.quadrant == Quadrant.automation_battlefield
                ]
                if auto_scenes:
                    auto_scenes.sort(key=lambda s: -s.lps_display)
                    lowest = min(top_3, key=lambda s: s.lps_display)
                    if auto_scenes[0].lps_display > lowest.lps_display - AUTO_REPLACEMENT_TOLERANCE:
                        top_3.remove(lowest)
                        top_3.append(auto_scenes[0])
                        # 重新排序
                        top_3.sort(key=self._sort_key)

        # 分配排名（PRD §4 — 🥇🥈🥉）
        for i, s in enumerate(top_3):
            s.rank = i + 1

        return ScenePriorityResult(
            total_candidates=len(candidates),
            eligible_count=len([s for s in all_scores if s.priority_tier <= 3]),
            all_scores=all_scores,
            top_3=top_3,
            fallback_triggered=fallback_triggered,
            fallback_reason=fallback_reason,
        )

    # ── 单场景评分 ──────────────────────────────────────

    def _score_one(self, candidate: ScenePriorityInput) -> ScenePriorityScore:
        """对单个候选场景计算完整四象限评分。

        PRD §3.3: LPS_最终 = LPS × κ, LPS_显示_最终 = LPS_最终 × 2
        """
        x = self._clamp_score(candidate.structuredness_x)
        y = self._clamp_score(candidate.complexity_y)

        qs = x * y
        lps = x * WEIGHT_X + (Y_INVERSION_BASE - y) * WEIGHT_Y_INV

        quadrant = self._classify_quadrant(x, y)
        tier = self._get_priority_tier(quadrant)

        kappa = self._get_industry_coefficient(candidate.industry)
        lps_final = round(lps * kappa, 4)
        lps_display = round(lps * kappa * LPS_DISPLAY_MULTIPLIER, 1)

        level = self._get_recommendation_level(lps_display)

        return ScenePriorityScore(
            scene_id=candidate.scene_id,
            scene_name=candidate.scene_name,
            category=candidate.category,
            structuredness_x=x,
            complexity_y=y,
            qs=qs,
            lps=round(lps, 4),
            lps_display=lps_display,
            lps_final=lps_final,
            industry_coefficient=kappa,
            quadrant=quadrant,
            priority_tier=tier,
            recommendation_level=level,
            recommendation_label=level.value,
            recommendation_template=QUADRANT_RECOMMENDATION_TEMPLATES.get(quadrant, ""),
        )

    # ── 象限分类（PRD §2.1）─────────────────────────────

    def _classify_quadrant(self, x: float, y: float) -> Quadrant:
        """根据 X/Y 坐标判定象限归属。"""
        if x >= QUADRANT_THRESHOLD and y >= QUADRANT_THRESHOLD:
            return Quadrant.ai_priority
        elif x >= QUADRANT_THRESHOLD and y < QUADRANT_THRESHOLD:
            return Quadrant.automation_battlefield
        elif x < QUADRANT_THRESHOLD and y >= QUADRANT_THRESHOLD:
            return Quadrant.human_ai_collab
        else:
            return Quadrant.human_reserved

    def _get_priority_tier(self, quadrant: Quadrant) -> int:
        """象限 → 推荐梯队映射（PRD §2.2）。

        自动化主战场(1) > AI优先区(2) > 人机协作区(3) > 人类保留区(4)
        """
        mapping = {
            Quadrant.automation_battlefield: 1,
            Quadrant.ai_priority: 2,
            Quadrant.human_ai_collab: 3,
            Quadrant.human_reserved: 4,
        }
        return mapping[quadrant]

    def _get_recommendation_level(self, lps_display: float) -> RecommendationLevel:
        """LPS_display → 推荐等级映射（PRD §2.3）。"""
        if lps_display >= IMMEDIATE_START_THRESHOLD:
            return RecommendationLevel.immediate_start
        elif lps_display >= PLAN_ADVANCE_THRESHOLD:
            return RecommendationLevel.plan_advance
        else:
            return RecommendationLevel.observe

    # ── 行业系数（PRD §3.3）─────────────────────────────

    def _get_industry_coefficient(self, industry: str) -> float:
        """根据行业文本匹配修正系数 κ，未匹配则返回默认 1.00。

        按键长度降序匹配，确保"制造业（流程型）"优先于"制造业"。
        """
        if not industry:
            return DEFAULT_INDUSTRY_COEFFICIENT
        sorted_keys = sorted(INDUSTRY_COEFFICIENTS.keys(), key=len, reverse=True)
        for key in sorted_keys:
            if key in industry:
                return INDUSTRY_COEFFICIENTS[key]
        return DEFAULT_INDUSTRY_COEFFICIENT

    # ── 启发式自动评分（PRD §1.1, §1.2）─────────────────

    def score_structuredness(self, text: str) -> int:
        """基于 NLP 信号关键词的启发式结构化程度评分。

        扫描文本中的信号关键词，按 5→1 优先级返回最高匹配分值。
        无匹配时默认返回 3（中度结构化）。
        """
        if not text:
            return 3
        normalized = self._normalize_text(text)
        for score in [5, 4, 3, 2, 1]:
            for signal in STRUCTUREDNESS_SIGNALS.get(score, []):
                if self._normalize_text(signal) in normalized:
                    return score
        return 3

    def score_complexity(self, text: str) -> int:
        """基于 NLP 信号关键词的启发式复杂程度评分。

        扫描文本中的信号关键词，按 5→1 优先级返回最高匹配分值。
        无匹配时默认返回 3（中等复杂度）。
        """
        if not text:
            return 3
        normalized = self._normalize_text(text)
        for score in [5, 4, 3, 2, 1]:
            for signal in COMPLEXITY_SIGNALS.get(score, []):
                if self._normalize_text(signal) in normalized:
                    return score
        return 3

    # ── 排序与平局打破（PRD §3.2）─────────────────────────

    def _sort_key(self, s: ScenePriorityScore) -> tuple[int, float, float, float]:
        """复合排序键：梯队升序 → LPS_display 降序 → X 降序 → QS 降序。

        与 PRD §3.2 打破平局规则完全对齐：
          1. 象限梯队数字更小者优先
          2. LPS_display 更高者优先
          3. 结构化程度 X 更高者优先
          4. QS 分更高者优先
          5. 仍相同 — 保持稳定排序顺序
        """
        return (s.priority_tier, -s.lps_display, -s.structuredness_x, -s.qs)

    # ── 工具方法 ────────────────────────────────────────

    @staticmethod
    def _clamp_score(value: float) -> float:
        """将分值限制在 1-5 范围内。"""
        return max(1.0, min(5.0, float(value)))

    @staticmethod
    def _normalize_text(text: str) -> str:
        """去除非字母数字/中文字符，转小写。"""
        import re

        return re.sub(r"[^\w\u4e00-\u9fff]+", "", text).lower()
