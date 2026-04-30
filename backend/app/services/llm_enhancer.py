"""LLM-enhanced versions of rule-based analysis services.

Each service tries LLM generation first, falls back to rule-based on failure.
Configuration: set LLM_MODE=live and provide OPENAI_API_KEY/OPENAI_MODEL.
"""

import json
import logging
import re
from typing import Any

from app.core.config import settings
from app.schemas.assessment import CanvasDiagnosisResult
from app.schemas.breakthrough import (
    BreakthroughElement,
    BreakthroughRecommendationResult,
)
from app.schemas.competitiveness import (
    CompetitivenessResult,
    CoreAdvantage,
    DeliveryStrategy,
    PointToLineConnection,
    VPReconstruction,
)
from app.schemas.direction import DirectionSuggestion

logger = logging.getLogger(__name__)

BREAKTHROUGH_SYSTEM = """
你是一位企业战略顾问，正在分析商业模式画布的薄弱环节。

任务：基于画布诊断数据，深度分析每个要素的薄弱程度和突破建议。

输出要求：
1. 为每个要素给出 0-100 的评分（越低越薄弱）
2. 推荐 3 个最需要优先突破的要素
3. 给出综合性的突破建议

输出 JSON 格式：
{
  "elements": [
    {"key": "key_partnerships", "title": "关键合作伙伴", "score": 35, "reason": "...", "ai_opportunity": "..."},
    ...9个要素
  ],
  "recommended_keys": ["key_partnerships", "channels", "cost_structure"],
  "overall_suggestion": "..."
}
""".strip()

DIRECTION_SYSTEM = """
你是一位企业创新顾问，需要为突破要素生成具体的创新方向。

任务：针对每个突破要素，给出 2-3 个具体的、可落地的创新方向。

输出 JSON 格式：
{
  "elements": [
    {
      "element_key": "key_partnerships",
      "element_title": "关键合作伙伴",
      "suggestions": [
        {
          "direction_id": "unique_id_1",
          "element_key": "key_partnerships",
          "title": "方向标题",
          "description": "一句话描述",
          "expected_impact": "预期影响",
          "data_needed": ["数据1", "数据2"],
          "related_scenario_categories": ["销售增长", "交付运营"]
        }
      ]
    }
  ],
  "total_suggestions": 6
}
""".strip()

COMPETITIVENESS_SYSTEM = """
你是一位企业战略顾问，正在做差异化竞争力分析。

任务：基于突破要素和选定的创新方向，生成完整的竞争力分析。

输出 JSON 格式：
{
  "vp_reconstruction": {
    "current_vp": "当前价值主张",
    "enhanced_vp": "增强型价值主张",
    "differentiation_points": ["差异点1", "差异点2"],
    "customer_value_shift": "客户价值转移路径描述"
  },
  "connections": [
    {
      "line_name": "竞争力线名称",
      "point_ids": [],
      "point_titles": ["方向1", "方向2"],
      "strategic_narrative": "战略叙事",
      "competitive_impact": "竞争力影响",
      "key_metrics": ["指标1", "指标2"]
    }
  ],
  "advantages": [
    {
      "advantage_name": "优势名称",
      "source_elements": ["来源要素"],
      "description": "优势描述",
      "barrier_level": "高/中/低"
    }
  ],
  "delivery_strategy": {
    "phase_1_quick_win": "阶段1快速验证",
    "phase_2_scale": "阶段2规模扩展",
    "phase_3_moat": "阶段3壁垒构建",
    "key_risks": ["风险1", "风险2"]
  },
  "overall_narrative": "总体判断..."
}
""".strip()


class LLMEnhancer:
    def __init__(self) -> None:
        self._client = None

    @property
    def _openai_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
        return self._client

    def _is_live_mode(self) -> bool:
        return settings.llm_mode == "live" and bool(settings.openai_api_key) and bool(settings.openai_model)

    def _call_llm(self, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
        try:
            response = self._openai_client.chat.completions.create(
                model=settings.openai_model,
                temperature=0.4,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                timeout=60,
            )
            raw = response.choices[0].message.content or ""
            json_str = self._extract_json(raw)
            return json.loads(json_str)
        except Exception as exc:
            logger.warning("LLM call failed for enhancer: %s", exc)
            return None

    @staticmethod
    def _extract_json(raw: str) -> str:
        raw = raw.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        return match.group(0) if match else raw

    def enhance_breakthrough(
        self,
        canvas_diagnosis: CanvasDiagnosisResult,
    ) -> BreakthroughRecommendationResult | None:
        if not self._is_live_mode():
            return None

        blocks_summary = "\n".join(
            f"- {b.title}({b.key}): 诊断={b.diagnosis[:60]}, 机会={b.ai_opportunity[:60]}"
            for b in canvas_diagnosis.canvas.blocks
        )
        user_prompt = f"""画布诊断数据：
整体评分: {canvas_diagnosis.overall_score}
薄弱模块: {', '.join(canvas_diagnosis.weakest_blocks)}

各模块详情：
{blocks_summary}

请基于以上数据生成突破要素推荐。"""

        result = self._call_llm(BREAKTHROUGH_SYSTEM, user_prompt)
        if not result:
            return None

        try:
            elements = [BreakthroughElement.model_validate(e) for e in result.get("elements", [])]
            if len(elements) != 9:
                return None
            return BreakthroughRecommendationResult(
                generation_mode="llm",
                elements=elements,
                recommended_keys=result.get("recommended_keys", [])[:3],
                overall_suggestion=result.get("overall_suggestion", ""),
            )
        except Exception as exc:
            logger.warning("Failed to parse LLM breakthrough response: %s", exc)
            return None

    def enhance_directions(
        self,
        canvas_diagnosis: CanvasDiagnosisResult,
        breakthrough_keys: list[str],
    ) -> list[DirectionSuggestion] | None:
        if not self._is_live_mode():
            return None

        from app.schemas.breakthrough import ELEMENT_KEY_TO_TITLE

        block_details = "\n".join(
            f"- {b.title}({b.key}): {b.diagnosis[:80]}, AI机会={b.ai_opportunity[:80]}"
            for b in canvas_diagnosis.canvas.blocks
            if b.key in breakthrough_keys
        )
        keys_display = "、".join(ELEMENT_KEY_TO_TITLE.get(k, k) for k in breakthrough_keys)

        user_prompt = f"""选定突破要素: {keys_display}

相关模块详情：
{block_details}

请为每个选定的突破要素生成 2-3 个具体的创新方向。direction_id 用英文下划线命名。"""

        result = self._call_llm(DIRECTION_SYSTEM, user_prompt)
        if not result:
            return None

        try:
            directions: list[DirectionSuggestion] = []
            for elem in result.get("elements", []):
                for s in elem.get("suggestions", []):
                    directions.append(DirectionSuggestion.model_validate(s))
            return directions if directions else None
        except Exception as exc:
            logger.warning("Failed to parse LLM direction response: %s", exc)
            return None

    def enhance_competitiveness(
        self,
        canvas_diagnosis: CanvasDiagnosisResult,
        breakthrough_keys: list[str],
        selected_directions: list[DirectionSuggestion],
    ) -> CompetitivenessResult | None:
        if not self._is_live_mode():
            return None

        from app.schemas.breakthrough import ELEMENT_KEY_TO_TITLE

        dir_summary = "\n".join(
            f"- [{d.element_key}] {d.title}: {d.description[:80]}"
            for d in selected_directions
        )
        keys_display = "、".join(ELEMENT_KEY_TO_TITLE.get(k, k) for k in breakthrough_keys)

        user_prompt = f"""突破要素: {keys_display}
画布评分: {canvas_diagnosis.overall_score}
薄弱模块: {', '.join(canvas_diagnosis.weakest_blocks)}

选定创新方向：
{dir_summary}

请生成完整的差异化竞争力分析，barrier_level 用 高/中/低 三个级别。"""

        result = self._call_llm(COMPETITIVENESS_SYSTEM, user_prompt)
        if not result:
            return None

        try:
            vp_raw = result.get("vp_reconstruction", {})
            vp = VPReconstruction.model_validate(vp_raw)

            connections = [
                PointToLineConnection.model_validate(c)
                for c in result.get("connections", [])
            ]
            advantages = [
                CoreAdvantage.model_validate(a)
                for a in result.get("advantages", [])
            ]
            strategy = DeliveryStrategy.model_validate(
                result.get("delivery_strategy", {})
            )
            return CompetitivenessResult(
                generation_mode="llm",
                vp_reconstruction=vp,
                connections=connections,
                advantages=advantages,
                delivery_strategy=strategy,
                overall_narrative=result.get("overall_narrative", ""),
            )
        except Exception as exc:
            logger.warning("Failed to parse LLM competitiveness response: %s", exc)
            return None
