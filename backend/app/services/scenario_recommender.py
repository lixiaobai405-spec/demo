import re
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field

from app.core.config import ROOT_DIR
from app.models.assessment import Assessment
from app.schemas.assessment import CompanyProfileResult, ScenarioRecommendationItem, ScenarioRecommendationResult
from app.schemas.scene_priority import ScenePriorityInput
from app.services.scene_priority_scorer import ScenePriorityScorer

SCENARIO_LIBRARY_PATH = ROOT_DIR / "knowledge" / "raw" / "ai_scenarios.yaml"


class ScenarioDefinition(BaseModel):
    id: str
    name: str
    category: str
    summary: str
    applicable_industries: list[str] = Field(default_factory=list)
    challenge_keywords: list[str] = Field(default_factory=list)
    goal_keywords: list[str] = Field(default_factory=list)
    data_keywords: list[str] = Field(default_factory=list)
    canvas_keywords: list[str] = Field(default_factory=list)
    data_requirements: list[str] = Field(default_factory=list)


class ScenarioLibrary(BaseModel):
    scenarios: list[ScenarioDefinition] = Field(default_factory=list)


@lru_cache(maxsize=1)
def load_scenario_library() -> ScenarioLibrary:
    raw_payload = yaml.safe_load(SCENARIO_LIBRARY_PATH.read_text(encoding="utf-8"))
    return ScenarioLibrary.model_validate(raw_payload)


class ScenarioRecommender:
    def recommend(
        self,
        assessment: Assessment,
        profile: CompanyProfileResult | None = None,
        direction_categories: list[str] | None = None,
    ) -> tuple[list[ScenarioRecommendationItem], int]:
        library = load_scenario_library()
        scored = [
            (self._calc_score(definition, assessment, profile, direction_categories), definition)
            for definition in library.scenarios
        ]
        scored.sort(key=lambda x: (-x[0], x[1].name))
        top_items = [
            self._build_item(definition, assessment, profile, direction_categories)
            for _, definition in scored[:3]
        ]
        return top_items, len(scored)

    def _build_item(
        self,
        definition: ScenarioDefinition,
        assessment: Assessment,
        profile: CompanyProfileResult | None,
        direction_categories: list[str] | None = None,
    ) -> ScenarioRecommendationItem:
        return ScenarioRecommendationItem(
            scenario_id=definition.id,
            name=definition.name,
            category=definition.category,
            summary=definition.summary,
            canvas_elements="、".join(definition.canvas_keywords[:3]) if definition.canvas_keywords else "",
            expected_effects=(
                f"通过{definition.name}，预期可{'、'.join(definition.goal_keywords[:3])}"
                if definition.goal_keywords
                else f"通过{definition.name}提升业务效率与竞争力"
            ),
            core_data_requirements=(
                definition.data_requirements[0]
                if definition.data_requirements
                else ""
            ),
        )

    def _calc_score(
        self,
        definition: ScenarioDefinition,
        assessment: Assessment,
        profile: CompanyProfileResult | None,
        direction_categories: list[str] | None = None,
    ) -> int:
        industry_text = self._normalize_text(assessment.industry)
        challenge_text = self._normalize_text(
            " ".join(
                filter(
                    None,
                    [
                        assessment.current_challenges,
                        "；".join(profile.key_challenges) if profile else "",
                        profile.digital_and_ai_readiness if profile else "",
                    ],
                )
            )
        )
        goal_text = self._normalize_text(
            " ".join(
                filter(
                    None,
                    [
                        assessment.ai_goals,
                        "；".join(profile.priority_ai_directions) if profile else "",
                    ],
                )
            )
        )
        data_text = self._normalize_text(
            " ".join(
                filter(
                    None,
                    [
                        assessment.available_data,
                        profile.operations_and_resources if profile else "",
                    ],
                )
            )
        )
        business_text = self._normalize_text(
            " ".join(
                filter(
                    None,
                    [
                        assessment.core_products,
                        assessment.target_customers,
                        assessment.notes,
                        profile.value_proposition if profile else "",
                        profile.customer_and_market if profile else "",
                    ],
                )
            )
        )

        industry_matches = self._find_matches(industry_text, definition.applicable_industries)
        challenge_matches = self._find_matches(challenge_text, definition.challenge_keywords)
        goal_matches = self._find_matches(goal_text, definition.goal_keywords)
        data_matches = self._find_matches(data_text, definition.data_keywords)
        business_matches = self._find_matches(business_text, definition.canvas_keywords)

        score = 5
        if industry_matches:
            score += 18
        elif "通用" in definition.applicable_industries:
            score += 8

        score += min(24, len(challenge_matches) * 7)
        score += min(24, len(goal_matches) * 7)
        score += min(16, len(data_matches) * 4)
        score += min(10, len(business_matches) * 5)

        if data_matches and (challenge_matches or goal_matches):
            score += 8
        if not data_matches:
            score -= 4
        if not challenge_matches and not goal_matches:
            score -= 6

        if direction_categories:
            for category in direction_categories:
                if category in definition.category or definition.category in category:
                    score += 10
                    break

        final_score = max(0, min(100, score))
        return final_score

    def _find_matches(self, source_text: str, keywords: list[str]) -> list[str]:
        matches: list[str] = []
        for keyword in keywords:
            if keyword == "通用":
                continue

            normalized_keyword = self._normalize_text(keyword)
            if normalized_keyword and normalized_keyword in source_text:
                matches.append(keyword)

        seen: set[str] = set()
        deduped_matches = []
        for match in matches:
            if match not in seen:
                deduped_matches.append(match)
                seen.add(match)
        return deduped_matches

    def recommend_with_priority(
        self,
        assessment: Assessment,
        profile: CompanyProfileResult | None = None,
        direction_categories: list[str] | None = None,
    ) -> ScenarioRecommendationResult:
        """使用四象限优先级评分引擎进行 Top 3 场景推荐。

        先运行关键词评分筛选候选场景，再通过 ScenePriorityScorer
        计算每个场景的结构化程度、复杂度及综合优先级，最终按
        梯队+LPS 排序返回 Top 3。
        """
        library = load_scenario_library()

        # Step 1：关键词评分
        scored = [
            (self._calc_score(definition, assessment, profile, direction_categories), definition)
            for definition in library.scenarios
        ]
        scored.sort(key=lambda x: (-x[0], x[1].name))

        # Step 2：构建四象限评分输入
        priority_scorer = ScenePriorityScorer()

        definition_map: dict[str, ScenarioDefinition] = {}
        candidates: list[ScenePriorityInput] = []
        for kw_score, definition in scored:
            definition_map[definition.id] = definition

            # 启发式自动评分 X/Y
            x = float(priority_scorer.score_structuredness(definition.summary + definition.category))
            y = float(priority_scorer.score_complexity(definition.summary + definition.category))

            candidates.append(
                ScenePriorityInput(
                    scene_id=definition.id,
                    scene_name=definition.name,
                    category=definition.category,
                    summary=definition.summary,
                    structuredness_x=x,
                    complexity_y=y,
                    industry=assessment.industry or "",
                    canvas_elements="、".join(definition.canvas_keywords[:3]) if definition.canvas_keywords else "",
                    expected_effects=(
                        f"通过{definition.name}，预期可{'、'.join(definition.goal_keywords[:3])}"
                        if definition.goal_keywords
                        else f"通过{definition.name}提升业务效率与竞争力"
                    ),
                    core_data_requirements=(
                        definition.data_requirements[0]
                        if definition.data_requirements
                        else ""
                    ),
                )
            )

        # Step 3：四象限优先级评分 + Top 3
        priority_result = priority_scorer.recommend_top3(candidates)

        # Step 4：转换为 ScenarioRecommendationItem，从原始 definition 补充内容字段
        top_scenarios: list[ScenarioRecommendationItem] = []
        for ps in priority_result.top_3:
            definition = definition_map.get(ps.scene_id)
            item = ScenarioRecommendationItem(
                scenario_id=ps.scene_id,
                name=ps.scene_name,
                category=ps.category,
                summary=definition.summary if definition else "",
                canvas_elements=(
                    "、".join(definition.canvas_keywords[:3])
                    if definition and definition.canvas_keywords
                    else ""
                ),
                expected_effects=(
                    f"通过{ps.scene_name}，预期可{'、'.join(definition.goal_keywords[:3])}"
                    if definition and definition.goal_keywords
                    else f"通过{ps.scene_name}提升业务效率与竞争力"
                ),
                core_data_requirements=(
                    definition.data_requirements[0]
                    if definition and definition.data_requirements
                    else ""
                ),
                priority_structuredness_x=ps.structuredness_x,
                priority_complexity_y=ps.complexity_y,
                priority_qs=ps.qs,
                priority_lps=ps.lps,
                priority_lps_display=ps.lps_display,
                priority_quadrant=ps.quadrant.value,
                priority_tier=ps.priority_tier,
                priority_recommendation=ps.recommendation_template,
            )
            top_scenarios.append(item)

        return ScenarioRecommendationResult(
            scoring_method="four_quadrant_v1",
            evaluated_count=priority_result.total_candidates,
            top_scenarios=top_scenarios,
            fallback_triggered=priority_result.fallback_triggered,
            fallback_reason=priority_result.fallback_reason,
        )

    def _normalize_text(self, text: str | None) -> str:
        if not text:
            return ""

        return re.sub(r"[^\w\u4e00-\u9fff]+", "", text).lower()
