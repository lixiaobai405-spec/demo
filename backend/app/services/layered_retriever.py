"""C2: Layered Retrieval — 行业→规模→痛点→方向 分层案例匹配

Architecture:
  Layer 1: Industry match (exact > sibling > general)
  Layer 2: Company size/scale proximity
  Layer 3: Pain point keyword overlap
  Layer 4: Direction / canvas block overlap + AI scenario relevance
  Bonus: RAG vector hybrid when available

Each layer produces a score component and explicit source annotation.
"""

import logging
from dataclasses import dataclass, field

from app.models.assessment import Assessment
from app.schemas.assessment import CanvasDiagnosisResult, ScenarioRecommendationResult

logger = logging.getLogger(__name__)

INDUSTRY_SIBLINGS: dict[str, list[str]] = {
    "制造": ["装备制造", "工业设备", "医疗器械", "制造业", "生产制造", "工业分销", "供应链"],
    "装备制造": ["制造", "工业设备", "制造业"],
    "医疗器械": ["制造", "设备制造", "医疗"],
    "零售": ["连锁零售", "消费品", "电商", "零售业"],
    "连锁零售": ["零售", "消费品", "电商"],
    "软件": ["B2B", "企业服务", "科技", "互联网", "SaaS"],
    "B2B软件": ["软件", "企业服务", "科技", "SaaS"],
    "工程服务": ["工程", "服务", "项目型"],
    "工业分销": ["供应链", "制造", "工业设备"],
    "区域服务": ["服务", "企业服务"],
    "企业服务": ["软件", "B2B", "服务", "SaaS"],
    "科技": ["软件", "互联网", "SaaS", "企业服务"],
    "互联网": ["科技", "软件", "电商"],
    "金融": ["银行", "保险", "支付", "金融服务"],
    "医疗": ["医疗器械", "医药", "健康"],
    "教育": ["在线教育", "培训"],
}

COMPANY_SIZE_LEVELS = {
    "微型": ["1-10人", "10-50人"],
    "小型": ["10-50人", "50-100人"],
    "中小型": ["50-100人", "100-200人"],
    "中型": ["100-200人", "200-500人"],
    "中大型": ["200-500人", "500-1000人"],
    "大型": ["500-1000人", "1000人以上"],
}


@dataclass
class LayerResult:
    layer_name: str
    score_contribution: float
    weight: float
    matched_labels: list[str] = field(default_factory=list)
    detail: str = ""


@dataclass
class LayeredMatchResult:
    case_id: str
    title: str
    industry: str
    summary: str
    final_score: float
    layers: list[LayerResult] = field(default_factory=list)
    retrieval_source: str = "layered_rule"
    source_summary: str = ""
    reference_points: list[str] = field(default_factory=list)
    data_foundation: list[str] = field(default_factory=list)
    cautions: list[str] = field(default_factory=list)


class LayeredRetriever:
    def __init__(self) -> None:
        self._rag_retriever = None

    def _get_rag_retriever(self):
        if self._rag_retriever is None:
            try:
                from app.rag.retriever import RAGRetriever
                self._rag_retriever = RAGRetriever()
            except Exception:
                self._rag_retriever = False
        return self._rag_retriever if self._rag_retriever is not False else None

    def retrieve(
        self,
        case_definitions: list,
        assessment: Assessment,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> list[LayeredMatchResult]:
        results: list[LayeredMatchResult] = []
        industry = self._norm(assessment.industry)
        size = self._norm(assessment.company_size)
        challenges = self._norm(assessment.current_challenges)
        ai_goals = self._norm(assessment.ai_goals)

        canvas_blocks_str = " ".join(
            f"{b.title} {b.diagnosis} {b.ai_opportunity}"
            for b in canvas_diagnosis.canvas.blocks
        )
        scenario_names = " ".join(s.name for s in scenario_recommendation.top_scenarios)
        top_scenarios = [s.name for s in scenario_recommendation.top_scenarios]

        for case_def in case_definitions:
            layers: list[LayerResult] = []

            applicable = [self._norm(i) for i in case_def.applicable_industries]
            case_industry = self._norm(case_def.industry)
            pain_keywords = case_def.pain_keywords
            canvas_blocks = case_def.canvas_blocks
            scenario_keywords = case_def.scenario_keywords

            layer1 = self._layer_industry(industry, case_industry, applicable)
            layers.append(layer1)

            layer2 = self._layer_scale(size, case_def)
            layers.append(layer2)

            layer3 = self._layer_pain(challenges, ai_goals, pain_keywords)
            layers.append(layer3)

            layer4 = self._layer_direction(
                canvas_blocks_str, scenario_names, top_scenarios,
                canvas_blocks, scenario_keywords,
            )
            layers.append(layer4)

            final_score = sum(l.score_contribution for l in layers)
            final_score = max(0.0, min(100.0, final_score))

            source_parts = []
            for l in layers:
                if l.matched_labels:
                    source_parts.append(f"[{l.layer_name}] {', '.join(l.matched_labels[:4])}")
            source_summary = " | ".join(source_parts) if source_parts else "通用参考"

            results.append(LayeredMatchResult(
                case_id=case_def.id,
                title=case_def.title,
                industry=case_def.industry,
                summary=case_def.summary,
                final_score=final_score,
                layers=layers,
                retrieval_source="layered_rule",
                source_summary=source_summary,
                reference_points=case_def.reference_points,
                data_foundation=case_def.data_foundation,
                cautions=case_def.cautions,
            ))

        results.sort(key=lambda r: r.final_score, reverse=True)
        return results[:3]

    def _layer_industry(
        self,
        assessment_industry: str,
        case_industry: str,
        applicable_industries: list[str],
    ) -> LayerResult:
        weight = 0.28
        ai = assessment_industry.lower()
        ci = case_industry.lower()
        ai_clean = self._norm(assessment_industry)

        if ci == ai or ci in ai or ai in ci:
            return LayerResult("行业匹配", 28.0, weight, [case_industry], "精确行业匹配 (28/28)")

        for applicable in applicable_industries:
            a = self._norm(applicable)
            if a == ai_clean:
                return LayerResult("行业匹配", 24.0, weight, [applicable], f"适用行业精确匹配 {applicable} (24/28)")
            if a in ai_clean or ai_clean in a:
                return LayerResult("行业匹配", 20.0, weight, [applicable], f"适用行业部分匹配 {applicable} (20/28)")

        siblings = INDUSTRY_SIBLINGS.get(ai_clean, [])
        for applicable in applicable_industries:
            for sib in siblings:
                if self._norm(applicable) in sib or sib in self._norm(applicable):
                    return LayerResult("行业匹配", 12.0, weight, [applicable], f"行业近亲匹配 {applicable} (12/28)")

        if "通用" in applicable_industries:
            return LayerResult("行业匹配", 8.0, weight, ["通用"], "通用行业 (8/28)")

        return LayerResult("行业匹配", 0.0, weight, [], "行业不匹配 (0/28)")

    def _layer_scale(
        self,
        assessment_size: str,
        case_def,
    ) -> LayerResult:
        weight = 0.12
        size_map: dict[str, int] = {
            "1-10人": 1, "10-50人": 2, "50-100人": 3,
            "100-200人": 4, "200-500人": 5,
            "500-1000人": 6, "1000人以上": 7,
        }
        assessment_level = None
        for label, ranges in COMPANY_SIZE_LEVELS.items():
            for r in ranges:
                if r in assessment_size:
                    assessment_level = label
                    break
            if assessment_level:
                break

        if assessment_level is None:
            return LayerResult("规模匹配", 6.0, weight, ["未知规模"], "默认为中等规模 (6/12)")

        case_size_str = getattr(case_def, "company_size", None)
        if case_size_str is None:
            return LayerResult("规模匹配", 8.0, weight, ["规模未标注"], "案例库未标注规模 (8/12)")

        case_level = None
        for label, ranges in COMPANY_SIZE_LEVELS.items():
            for r in ranges:
                if r in str(case_size_str):
                    case_level = label
                    break
            if case_level:
                break

        if case_level and assessment_level:
            levels_order = ["微型", "小型", "中小型", "中型", "中大型", "大型"]
            if assessment_level == case_level:
                return LayerResult("规模匹配", 12.0, weight, [assessment_level], "规模完全匹配 (12/12)")
            ai_idx = levels_order.index(assessment_level) if assessment_level in levels_order else -1
            ci_idx = levels_order.index(case_level) if case_level in levels_order else -1
            if ai_idx >= 0 and ci_idx >= 0 and abs(ai_idx - ci_idx) <= 1:
                return LayerResult("规模匹配", 8.0, weight, [assessment_level, case_level], "规模接近 (8/12)")
            if ai_idx >= 0 and ci_idx >= 0 and abs(ai_idx - ci_idx) <= 2:
                return LayerResult("规模匹配", 5.0, weight, [assessment_level, case_level], "规模存在差距 (5/12)")

        return LayerResult("规模匹配", 3.0, weight, [assessment_level or "未知"], "规模有较大差距 (3/12)")

    def _layer_pain(
        self,
        challenges: str,
        ai_goals: str,
        pain_keywords: list[str],
    ) -> LayerResult:
        weight = 0.30
        combined = f"{challenges} {ai_goals}"
        match_count = 0
        matched: list[str] = []
        for kw in pain_keywords:
            if kw in combined:
                match_count += 1
                matched.append(kw)

        score = min(30.0, match_count * 6.0)
        return LayerResult("痛点匹配", score, weight, matched, f"命中{match_count}个痛点关键词 ({score:.0f}/30)")

    def _layer_direction(
        self,
        canvas_blocks_str: str,
        scenario_names: str,
        top_scenarios: list[str],
        case_canvas_blocks: list[str],
        case_scenario_keywords: list[str],
    ) -> LayerResult:
        weight = 0.30
        canvas_matches = 0
        matched_canvas: list[str] = []
        for cb in case_canvas_blocks:
            if cb in canvas_blocks_str:
                canvas_matches += 1
                matched_canvas.append(cb)

        scenario_matches = 0
        matched_scenarios: list[str] = []
        for sk in case_scenario_keywords:
            if sk in scenario_names or any(sk in ts for ts in top_scenarios):
                scenario_matches += 1
                matched_scenarios.append(sk)

        score_canvas = min(15.0, canvas_matches * 5.0)
        score_scenario = min(15.0, scenario_matches * 5.0)
        total = score_canvas + score_scenario

        bonus = 5.0 if canvas_matches and scenario_matches else 0.0
        total += bonus

        matched_labels = matched_canvas + matched_scenarios
        return LayerResult("方向匹配", total, weight, matched_labels,
            f"画布{canvas_matches}场景{scenario_matches}命中 ({total:.0f}/35)")

    @staticmethod
    def _norm(text: str | None) -> str:
        if not text:
            return ""
        return text.strip().lower().replace(" ", "").replace("\u3000", "")
