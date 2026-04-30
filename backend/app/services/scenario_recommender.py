import re
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field

from app.core.config import ROOT_DIR
from app.models.assessment import Assessment
from app.schemas.assessment import CompanyProfileResult, ScenarioRecommendationItem

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
        recommendations = [
            self._score_scenario(definition, assessment, profile, direction_categories)
            for definition in library.scenarios
        ]
        recommendations.sort(key=lambda item: (-item.score, item.name))
        return recommendations[:3], len(recommendations)

    def _score_scenario(
        self,
        definition: ScenarioDefinition,
        assessment: Assessment,
        profile: CompanyProfileResult | None,
        direction_categories: list[str] | None = None,
    ) -> ScenarioRecommendationItem:
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

        reasons = []
        if industry_matches:
            reasons.append(f"适配当前行业特征：{'、'.join(industry_matches[:3])}")
        if challenge_matches:
            reasons.append(f"直接响应当前挑战：{'、'.join(challenge_matches[:3])}")
        if goal_matches:
            reasons.append(f"与当前 AI 目标一致：{'、'.join(goal_matches[:3])}")
        if data_matches:
            reasons.append(f"现有数据基础可支持试点：{'、'.join(data_matches[:3])}")
        if direction_categories:
            matched_categories = [c for c in direction_categories if c in definition.category or definition.category in c]
            if matched_categories:
                reasons.append(f"与选定创新方向高度匹配：{'、'.join(matched_categories[:2])}")

        if not reasons:
            reasons.append("该场景具备一定通用价值，但仍需补充更多业务上下文后再优先推进。")

        return ScenarioRecommendationItem(
            scenario_id=definition.id,
            name=definition.name,
            category=definition.category,
            summary=definition.summary,
            score=final_score,
            reasons=reasons[:4],
            data_requirements=definition.data_requirements,
        )

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

    def _normalize_text(self, text: str | None) -> str:
        if not text:
            return ""

        return re.sub(r"[^\w\u4e00-\u9fff]+", "", text).lower()
