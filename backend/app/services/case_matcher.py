import re
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field

from app.core.config import ROOT_DIR
from app.models.assessment import Assessment
from app.schemas.assessment import (
    CanvasDiagnosisResult,
    CaseMatchItem,
    CompanyProfileResult,
    ScenarioRecommendationResult,
)
from app.services.layered_retriever import LayeredRetriever

CASE_LIBRARY_PATH = ROOT_DIR / "knowledge" / "raw" / "industry_cases.yaml"


class IndustryCaseDefinition(BaseModel):
    id: str
    title: str
    industry: str
    applicable_industries: list[str] = Field(default_factory=list)
    summary: str
    pain_keywords: list[str] = Field(default_factory=list)
    canvas_blocks: list[str] = Field(default_factory=list)
    scenario_keywords: list[str] = Field(default_factory=list)
    reference_points: list[str] = Field(default_factory=list)
    data_foundation: list[str] = Field(default_factory=list)
    cautions: list[str] = Field(default_factory=list)


class IndustryCaseLibrary(BaseModel):
    cases: list[IndustryCaseDefinition] = Field(default_factory=list)


@lru_cache(maxsize=1)
def load_case_library() -> IndustryCaseLibrary:
    raw_payload = yaml.safe_load(CASE_LIBRARY_PATH.read_text(encoding="utf-8"))
    return IndustryCaseLibrary.model_validate(raw_payload)


class CaseMatcher:
    LAYERED_MODE = True

    def match(
        self,
        assessment: Assessment,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> tuple[list[CaseMatchItem], int]:
        library = load_case_library()
        cases = library.cases

        if self.LAYERED_MODE:
            return self._match_layered(
                cases, assessment, canvas_diagnosis, scenario_recommendation
            )

        return self._match_legacy(
            cases, assessment, profile, canvas_diagnosis, scenario_recommendation
        )

    def _match_layered(
        self,
        case_definitions: list[IndustryCaseDefinition],
        assessment: Assessment,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> tuple[list[CaseMatchItem], int]:
        retriever = LayeredRetriever()
        layered_results = retriever.retrieve(
            case_definitions,
            assessment,
            canvas_diagnosis,
            scenario_recommendation,
        )

        items: list[CaseMatchItem] = []
        for lr in layered_results:
            pain_matches: list[str] = []
            canvas_matches: list[str] = []
            scenario_matches: list[str] = []
            for layer in lr.layers:
                if layer.layer_name == "痛点匹配":
                    pain_matches = [m for m in layer.matched_labels if m not in canvas_matches and m not in scenario_matches]
                elif layer.layer_name == "方向匹配":
                    for m in layer.matched_labels:
                        if m in [
                            "关键活动", "关键资源", "成本结构", "客户关系",
                            "收入来源", "客户细分", "渠道通路", "关键合作伙伴", "价值主张",
                        ]:
                            canvas_matches.append(m)
                        else:
                            scenario_matches.append(m)

            reasons: list[str] = []
            for layer in lr.layers:
                if layer.matched_labels:
                    reasons.append(f"[{layer.layer_name}] {layer.detail}")

            items.append(CaseMatchItem(
                case_id=lr.case_id,
                title=lr.title,
                industry=lr.industry,
                summary=lr.summary,
                fit_score=int(lr.final_score),
                matched_pain_points=pain_matches[:5],
                matched_canvas_blocks=canvas_matches[:5],
                matched_scenarios=scenario_matches[:5],
                match_reasons=reasons if reasons else ["该案例与当前企业存在一定通用参考价值。"],
                reference_points=lr.reference_points,
                data_foundation=lr.data_foundation,
                cautions=lr.cautions,
                retrieval_source=lr.retrieval_source,
                source_summary=lr.source_summary,
            ))

        items.sort(key=lambda x: (-x.fit_score, x.title))
        return items[:3], len(case_definitions)

    def _match_legacy(
        self,
        case_definitions: list[IndustryCaseDefinition],
        assessment: Assessment,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> tuple[list[CaseMatchItem], int]:
        matches = [
            self._score_case(
                definition,
                assessment,
                profile,
                canvas_diagnosis,
                scenario_recommendation,
            )
            for definition in case_definitions
        ]
        matches.sort(key=lambda item: (-item.fit_score, item.title))
        return matches[:3], len(case_definitions)

    def _score_case(
        self,
        definition: IndustryCaseDefinition,
        assessment: Assessment,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> CaseMatchItem:
        industry_text = self._normalize_text(assessment.industry)
        pain_text = self._normalize_text(
            " ".join(
                filter(
                    None,
                    [
                        assessment.current_challenges,
                        " ".join(profile.key_challenges),
                        profile.digital_and_ai_readiness,
                    ],
                )
            )
        )
        canvas_text = self._normalize_text(
            " ".join(
                block.title + " " + block.diagnosis + " " + block.ai_opportunity
                for block in canvas_diagnosis.canvas.blocks
            )
            + " "
            + " ".join(canvas_diagnosis.weakest_blocks)
            + " "
            + " ".join(canvas_diagnosis.recommended_focus)
        )
        scenario_text = self._normalize_text(
            " ".join(
                item.name + " " + item.category + " " + item.summary
                for item in scenario_recommendation.top_scenarios
            )
        )

        industry_matches = self._find_matches(
            industry_text,
            definition.applicable_industries,
        )
        definition_industry_match = self._normalize_text(definition.industry)
        pain_matches = self._find_matches(pain_text, definition.pain_keywords)
        canvas_matches = self._find_matches(canvas_text, definition.canvas_blocks)
        scenario_matches = self._find_matches(
            scenario_text,
            definition.scenario_keywords,
        )

        score = 5
        if industry_matches:
            score += 28
        elif "通用" in definition.applicable_industries:
            score += 8
        else:
            score -= 10

        if definition_industry_match and definition_industry_match in industry_text:
            score += 12

        score += min(28, len(pain_matches) * 7)
        score += min(18, len(canvas_matches) * 6)
        score += min(18, len(scenario_matches) * 6)

        if industry_matches and (pain_matches or scenario_matches):
            score += 10
        if canvas_matches and scenario_matches:
            score += 6
        if not scenario_matches:
            score -= 4
        if not pain_matches:
            score -= 2

        fit_score = max(0, min(100, score))

        reasons: list[str] = []
        if industry_matches:
            reasons.append(f"行业匹配：{', '.join(industry_matches[:3])}")
        if pain_matches:
            reasons.append(f"痛点匹配：{', '.join(pain_matches[:3])}")
        if canvas_matches:
            reasons.append(f"画布格子匹配：{', '.join(canvas_matches[:3])}")
        if scenario_matches:
            reasons.append(f"推荐场景匹配：{', '.join(scenario_matches[:3])}")
        if not reasons:
            reasons.append("该案例与当前企业存在一定通用参考价值，但仍需补充更细业务信息后再判断优先级。")

        return CaseMatchItem(
            case_id=definition.id,
            title=definition.title,
            industry=definition.industry,
            summary=definition.summary,
            fit_score=fit_score,
            matched_pain_points=pain_matches,
            matched_canvas_blocks=canvas_matches,
            matched_scenarios=scenario_matches,
            match_reasons=reasons,
            reference_points=definition.reference_points,
            data_foundation=definition.data_foundation,
            cautions=definition.cautions,
        )

    def _find_matches(self, source_text: str, keywords: list[str]) -> list[str]:
        matches: list[str] = []
        for keyword in keywords:
            if keyword == "通用":
                continue

            normalized_keyword = self._normalize_text(keyword)
            if normalized_keyword and normalized_keyword in source_text:
                matches.append(keyword)

        deduped: list[str] = []
        seen: set[str] = set()
        for match in matches:
            if match not in seen:
                deduped.append(match)
                seen.add(match)
        return deduped

    def _normalize_text(self, text: str | None) -> str:
        if not text:
            return ""

        return re.sub(r"[^\w\u4e00-\u9fff]+", "", text).lower()
