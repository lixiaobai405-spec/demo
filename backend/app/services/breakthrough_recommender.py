import json

from app.schemas.assessment import CanvasDiagnosisResult
from app.schemas.breakthrough import (
    BREAKTHROUGH_ELEMENTS,
    BreakthroughElement,
    BreakthroughRecommendationResult,
)


class BreakthroughRecommender:
    CANVAS_KEY_SCORE_WEIGHTS = {
        "待补充": -3,
        "缺失": -2,
        "不完整": -2,
        "不足": -2,
        "不清晰": -2,
    }

    def recommend(
        self,
        canvas_diagnosis: CanvasDiagnosisResult,
    ) -> BreakthroughRecommendationResult:
        elements = self._score_elements(canvas_diagnosis)
        sorted_elements = sorted(elements, key=lambda e: e.score)
        recommended_keys = [e.key for e in sorted_elements[:3]]

        if len(recommended_keys) >= 2:
            suggestion = (
                f"系统建议优先突破「{ELEMENT_KEY_TO_TITLE_LOCAL.get(recommended_keys[0], recommended_keys[0])}」"
                f"和「{ELEMENT_KEY_TO_TITLE_LOCAL.get(recommended_keys[1], recommended_keys[1])}」"
                + (
                    f"，同时关注「{ELEMENT_KEY_TO_TITLE_LOCAL.get(recommended_keys[2], recommended_keys[2])}」"
                    f"作为第三突破方向。"
                )
            )
        elif len(recommended_keys) == 1:
            suggestion = f"系统建议优先突破「{ELEMENT_KEY_TO_TITLE_LOCAL.get(recommended_keys[0], recommended_keys[0])}」。"
        else:
            suggestion = "请根据画布诊断结果手动选择 2-3 个最想突破的要素。"

        return BreakthroughRecommendationResult(
            generation_mode="rule_based",
            elements=sorted_elements,
            recommended_keys=recommended_keys,
            overall_suggestion=suggestion,
        )

    def _score_elements(
        self,
        canvas_diagnosis: CanvasDiagnosisResult,
    ) -> list[BreakthroughElement]:
        block_map = {
            block.key: block
            for block in canvas_diagnosis.canvas.blocks
        }

        element_map = {item["key"]: item for item in BREAKTHROUGH_ELEMENTS}
        elements: list[BreakthroughElement] = []

        weakest_set = set(canvas_diagnosis.weakest_blocks)

        for item in BREAKTHROUGH_ELEMENTS:
            key = item["key"]
            title = item["title"]
            block = block_map.get(key)
            if block is None:
                elements.append(
                    BreakthroughElement(
                        key=key,
                        title=title,
                        score=50,
                        reason="诊断数据缺失，无法评分。",
                        ai_opportunity="待补充画布诊断后分析。",
                    )
                )
                continue

            score = self._score_single_element(block.diagnosis, block.missing_information)

            if title in weakest_set:
                score = max(0, score - 10)

            reason = self._build_reason(title, block.diagnosis, block.missing_information, score)
            elements.append(
                BreakthroughElement(
                    key=key,
                    title=title,
                    score=score,
                    reason=reason,
                    ai_opportunity=block.ai_opportunity,
                )
            )

        return elements

    def _score_single_element(self, diagnosis: str, missing_info: str) -> int:
        base_score = 70
        combined_text = f"{diagnosis} {missing_info}"

        for keyword, penalty in self.CANVAS_KEY_SCORE_WEIGHTS.items():
            count = combined_text.count(keyword)
            base_score += count * penalty

        return max(10, min(100, base_score))

    def _build_reason(
        self,
        title: str,
        diagnosis: str,
        missing_info: str,
        score: int,
    ) -> str:
        if score <= 30:
            return f"「{title}」当前成熟度较低，信息缺口明显，是需要优先夯实的基础要素。"
        if score <= 50:
            return f"「{title}」存在明显短板，突破后可显著提升整体商业模型协同性。"
        if score <= 65:
            return f"「{title}」具备一定基础，但仍有结构化优化空间，可作为中层突破目标。"
        return f"「{title}」当前状态相对健康，可作为长期优化方向而非近期突破重点。"


ELEMENT_KEY_TO_TITLE_LOCAL = {
    "key_partnerships": "关键合作伙伴",
    "key_activities": "关键业务活动",
    "key_resources": "关键资源",
    "value_propositions": "价值主张",
    "customer_relationships": "客户关系",
    "channels": "渠道通路",
    "customer_segments": "客户细分",
    "cost_structure": "成本结构",
    "revenue_streams": "收入来源",
}
