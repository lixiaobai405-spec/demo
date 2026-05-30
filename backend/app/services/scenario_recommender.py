import re
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field

from app.core.config import ROOT_DIR
from app.models.assessment import Assessment
from app.schemas.assessment import (
    CompanyProfileResult,
    ScenarioBenefit,
    ScenarioRecommendationItem,
    ScenarioRecommendationResult,
    ScenarioResource,
)
from app.schemas.scene_priority import ScenePriorityInput
from app.services.scene_priority_scorer import ScenePriorityScorer

SCENARIO_LIBRARY_PATH = ROOT_DIR / "knowledge" / "raw" / "ai_scenarios.yaml"
MAX_POSITIONING_LENGTH = 15
MAX_SCENARIO_POOL_SIZE = 18

_CANVAS_META: dict[str, tuple[str, str, str]] = {
    "客户细分": ("客户细分（CS）", "customer_segments", "客户细分 CS"),
    "价值主张": ("价值主张（VP）", "value_propositions", "价值主张 VP"),
    "渠道": ("渠道通路（CH）", "channels", "渠道通路 CH"),
    "渠道通路": ("渠道通路（CH）", "channels", "渠道通路 CH"),
    "客户关系": ("客户关系（CR）", "customer_relationships", "客户关系 CR"),
    "收入来源": ("收入来源（R$）", "revenue_streams", "收入来源 R$"),
    "关键资源": ("关键资源（KR）", "key_resources", "关键资源 KR"),
    "核心资源": ("关键资源（KR）", "key_resources", "关键资源 KR"),
    "关键活动": ("关键业务（KA）", "key_activities", "关键业务 KA"),
    "关键业务": ("关键业务（KA）", "key_activities", "关键业务 KA"),
    "重要合作": ("重要合作（KP）", "key_partnerships", "重要合作 KP"),
    "关键合作伙伴": ("重要合作（KP）", "key_partnerships", "重要合作 KP"),
    "成本结构": ("成本结构（C$）", "cost_structure", "成本结构 C$"),
}


def _compact_one_liner(value: str, max_len: int = MAX_POSITIONING_LENGTH) -> str:
    text = re.sub(r"\s+", "", (value or "").strip())
    if not text:
        return ""
    text = re.split(r"[。；;]", text, maxsplit=1)[0]
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip("，、；;。")


def _benefit_text(goal: str) -> str:
    goal = goal.strip()
    if goal.startswith(("提升", "提高", "优化", "降低", "减少", "稳定", "增加", "缩短")):
        return f"有望{goal}"
    return f"有望提升{goal}"


# ── 轻量预期价值量化（P2.1）────────────────────────────

_QUANTIFIED_EFFECTS: dict[str, list[str]] = {
    "销售增长": [
        "预计提升 10%-25% 销售转化效率",
        "预计将线索响应时间从数小时缩短至分钟级",
    ],
    "售前效率": [
        "预计缩短 30%-50% 方案准备时间",
        "预计报价响应从 2-3 天压缩至 4-8 小时",
    ],
    "知识管理": [
        "预计减少 40%-60% 重复咨询",
        "预计知识检索时间从 30 分钟降至秒级",
    ],
    "交付运营": [
        "预计降低 20%-35% 交付延期风险",
        "预计提升 15%-25% 订单履约准时率",
    ],
    "生产运营": [
        "预计减少 15%-30% 非计划停机时间",
        "预计提升 10%-20% 产能利用率",
    ],
    "供应链": [
        "预计降低 20%-35% 库存积压",
        "预计提升 15%-25% 采购成本优化空间",
    ],
    "客户服务": [
        "预计缩短 40%-60% 客服响应时间",
        "预计降低 15%-25% 工单转人工率",
    ],
    "客户经营": [
        "预计提升 10%-20% 客户续约率",
        "预计提前 14-30 天识别流失风险",
    ],
    "财务经营": [
        "预计降低 15%-25% 逾期回款比例",
        "预计缩短 20%-35% 平均回款天数",
    ],
    "风险控制": [
        "预计缩短 50%-70% 合同审阅时间",
        "预计降低 20%-30% 合同条款遗漏风险",
    ],
    "人力资源": [
        "预计缩短 50%-70% 简历筛选时间",
        "预计提升 10%-20% 面试匹配精准度",
    ],
    "市场营销": [
        "预计提升 15%-25% 投放 ROI",
        "预计缩短 30%-50% 内容生产周期",
    ],
    "零售运营": [
        "预计提升 10%-20% 门店库存周转",
        "预计降低 15%-25% 缺货率",
    ],
    "管理分析": [
        "预计缩短 40%-60% 经营分析报告生成时间",
        "预计将异常发现时效从 T+3 天提升至实时",
    ],
    "协同办公": [
        "预计减少 20%-35% 跨部门信息遗漏",
        "预计缩短 30%-50% 会议行动项闭环时间",
    ],
}


def _build_quantified_effect(name: str, category: str, goal_keywords: list[str] | None) -> str:
    """构建预期价值量化描述，优先使用区间化数字，保留原有场景文案。"""
    base_text = (
        f"通过{name}，预期可{'、'.join(goal_keywords[:3])}"
        if goal_keywords
        else f"通过{name}提升业务效率与竞争力"
    )
    quant_lines = _QUANTIFIED_EFFECTS.get(category)
    if quant_lines:
        base_text = f"{base_text}。" + "；".join(quant_lines)
    return base_text


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
    structuredness_x: float | None = None
    complexity_y: float | None = None


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
        breakthrough_labels: list[str] | None = None,
        direction_titles: list[str] | None = None,
    ) -> tuple[list[ScenarioRecommendationItem], int]:
        library = load_scenario_library()
        scored = [
            (self._calc_score(definition, assessment, profile, direction_categories), definition)
            for definition in library.scenarios
        ]
        scored.sort(key=lambda x: (-x[0], x[1].name))
        top_items = [
            self._build_item(
                definition,
                assessment,
                profile,
                direction_categories,
                breakthrough_labels,
                direction_titles,
            )
            for _, definition in scored[:3]
        ]
        return top_items, len(scored)

    def _build_item(
        self,
        definition: ScenarioDefinition,
        assessment: Assessment,
        profile: CompanyProfileResult | None,
        direction_categories: list[str] | None = None,
        breakthrough_labels: list[str] | None = None,
        direction_titles: list[str] | None = None,
    ) -> ScenarioRecommendationItem:
        canvas_element, canvas_key, _ = self._resolve_canvas_meta(definition)
        return ScenarioRecommendationItem(
            scenario_id=definition.id,
            name=definition.name,
            category=definition.category,
            summary=self._build_template_summary(
                definition,
                direction_titles,
                breakthrough_labels,
            ),
            canvas_elements=self._build_canvas_element_text(
                definition,
                breakthrough_labels,
            ),
            expected_effects=self._build_effect_text(
                definition,
                direction_titles,
            ),
            core_data_requirements=self._build_data_requirement_text(definition),
            canvas_element=canvas_element,
            canvas_key=canvas_key,
            positioning=self._build_positioning(definition),
            value_dimensions=[],
            value_text=self._build_value_text(
                definition,
                direction_titles,
                breakthrough_labels,
            ),
            benefits=self._build_benefits(definition),
            resources=self._build_resources(definition),
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
            matched_count = 0
            for category in direction_categories:
                if category in definition.category or definition.category in category:
                    matched_count += 1
            score += min(36, matched_count * 12)

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
        breakthrough_labels: list[str] | None = None,
        direction_titles: list[str] | None = None,
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

        # 构建企业侧上下文文本，用于辅助 X/Y 评分
        enterprise_text = self._normalize_text(
            " ".join(
                filter(
                    None,
                    [
                        assessment.available_data,
                        assessment.current_challenges,
                        assessment.ai_goals,
                        profile.digital_and_ai_readiness if profile else "",
                        "；".join(profile.key_challenges) if profile else "",
                        "；".join(profile.priority_ai_directions) if profile else "",
                        profile.operations_and_resources if profile else "",
                    ],
                )
            )
        )
        direction_text = self._normalize_text(
            " ".join(direction_categories) if direction_categories else ""
        )

        definition_map: dict[str, ScenarioDefinition] = {}
        candidates: list[ScenePriorityInput] = []
        for kw_score, definition in scored:
            definition_map[definition.id] = definition

            # 构建场景侧评分上下文
            scene_text = self._normalize_text(
                " ".join(
                    filter(
                        None,
                        [
                            definition.summary,
                            definition.category,
                            " ".join(definition.data_requirements),
                            " ".join(definition.canvas_keywords),
                        ],
                    )
                )
            )

            # X（结构化程度）：优先使用场景库基准分，缺失时用 NLP 关键词评分兜底
            if definition.structuredness_x is not None and 1 <= definition.structuredness_x <= 5:
                x = float(definition.structuredness_x)
            else:
                x_context = " ".join(filter(None, [enterprise_text, scene_text, direction_text]))
                x = float(priority_scorer.score_structuredness(x_context))

            # Y（实施复杂度）：优先使用场景库基准分，缺失时用 NLP 关键词评分兜底
            if definition.complexity_y is not None and 1 <= definition.complexity_y <= 5:
                y = float(definition.complexity_y)
            else:
                y_context = " ".join(filter(None, [scene_text, enterprise_text]))
                y = float(priority_scorer.score_complexity(y_context))

            candidates.append(
                ScenePriorityInput(
                    scene_id=definition.id,
                    scene_name=definition.name,
                    category=definition.category,
                    summary=self._build_template_summary(
                        definition,
                        direction_titles,
                        breakthrough_labels,
                    ),
                    structuredness_x=x,
                    complexity_y=y,
                    industry=assessment.industry or "",
                    canvas_elements=self._build_canvas_element_text(
                        definition,
                        breakthrough_labels,
                    ),
                    expected_effects=self._build_effect_text(
                        definition,
                        direction_titles,
                    ),
                    core_data_requirements=self._build_data_requirement_text(definition),
                )
            )

        # Step 3：四象限优先级评分 + Top 3
        priority_result = priority_scorer.recommend_top3(candidates)

        # Step 4：转换为 ScenarioRecommendationItem，从原始 definition 补充内容字段
        def _score_to_item(ps, definition) -> ScenarioRecommendationItem:
            canvas_element, canvas_key, _ = (
                self._resolve_canvas_meta(definition)
                if definition
                else ("", "", "")
            )
            return ScenarioRecommendationItem(
                scenario_id=ps.scene_id,
                name=ps.scene_name,
                category=ps.category,
                summary=(
                    self._build_template_summary(
                        definition,
                        direction_titles,
                        breakthrough_labels,
                    )
                    if definition
                    else ""
                ),
                canvas_elements=(
                    self._build_canvas_element_text(definition, breakthrough_labels)
                    if definition
                    else ""
                ),
                expected_effects=(
                    self._build_effect_text(definition, direction_titles)
                    if definition
                    else ""
                ),
                core_data_requirements=(
                    self._build_data_requirement_text(definition)
                    if definition
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
                industry_coefficient=ps.industry_coefficient,
                recommendation_level=ps.recommendation_level.value if ps.recommendation_level else None,
                canvas_element=canvas_element,
                canvas_key=canvas_key,
                positioning=self._build_positioning(definition) if definition else "",
                value_dimensions=[],
                value_text=(
                    self._build_value_text(
                        definition,
                        direction_titles,
                        breakthrough_labels,
                    )
                    if definition
                    else ""
                ),
                benefits=self._build_benefits(definition) if definition else [],
                resources=self._build_resources(definition) if definition else [],
            )

        top_scenarios = [
            _score_to_item(ps, definition_map.get(ps.scene_id))
            for ps in priority_result.top_3
        ]
        all_scores = [
            _score_to_item(ps, definition_map.get(ps.scene_id))
            for ps in priority_result.all_scores
        ]
        all_scores = self._limit_scenario_pool(all_scores, top_scenarios)

        return ScenarioRecommendationResult(
            scoring_method="four_quadrant_v1",
            evaluated_count=len(all_scores),
            top_scenarios=top_scenarios,
            all_scores=all_scores,
        )

    def _limit_scenario_pool(
        self,
        all_scores: list[ScenarioRecommendationItem],
        top_scenarios: list[ScenarioRecommendationItem],
    ) -> list[ScenarioRecommendationItem]:
        top_ids = {item.scenario_id for item in top_scenarios}

        ranked = sorted(
            all_scores,
            key=lambda item: (
                item.scenario_id not in top_ids,
                -(item.priority_lps_display or 0),
                -(item.priority_qs or 0),
                item.name,
            ),
        )
        return ranked[:MAX_SCENARIO_POOL_SIZE]

    def _build_template_summary(
        self,
        definition: ScenarioDefinition,
        direction_titles: list[str] | None,
        breakthrough_labels: list[str] | None,
    ) -> str:
        directions = self._join_values(direction_titles, "、", "已确认方向")
        breakthroughs = self._join_values(breakthrough_labels, "、", "当前突破要素")
        base_summary = definition.summary.rstrip("。；; ")
        return (
            f"围绕“{directions}”，结合“{breakthroughs}”，在{definition.category}环节布局“{definition.name}”，"
            f"{base_summary}。"
        )

    def _build_canvas_element_text(
        self,
        definition: ScenarioDefinition,
        breakthrough_labels: list[str] | None,
    ) -> str:
        breakthroughs = self._join_values(
            breakthrough_labels,
            "、",
            "待补充突破要素",
        )
        canvas_keywords = self._join_values(
            definition.canvas_keywords[:3],
            "、",
            "待补充画布模块",
        )
        return f"对应突破要素：{breakthroughs}；关联画布模块：{canvas_keywords}"

    def _build_effect_text(
        self,
        definition: ScenarioDefinition,
        direction_titles: list[str] | None,
    ) -> str:
        directions = self._join_values(direction_titles, "、", "已确认方向")
        quantified = _build_quantified_effect(
            definition.name,
            definition.category,
            definition.goal_keywords,
        ).rstrip("。；; ")
        return f"支撑方向：{directions}；{quantified}。"

    def _build_data_requirement_text(self, definition: ScenarioDefinition) -> str:
        return f"关键数据：{self._join_values(definition.data_requirements[:3], '、', '待补充数据口径')}"

    def _resolve_canvas_meta(self, definition: ScenarioDefinition) -> tuple[str, str, str]:
        for keyword in definition.canvas_keywords:
            normalized = keyword.strip()
            if normalized in _CANVAS_META:
                return _CANVAS_META[normalized]
        return definition.category, "", definition.category

    def _build_positioning(self, definition: ScenarioDefinition) -> str:
        return (
            _compact_one_liner(definition.summary)
            or _compact_one_liner(definition.name)
            or definition.category
        )

    def _build_value_text(
        self,
        definition: ScenarioDefinition,
        direction_titles: list[str] | None,
        breakthrough_labels: list[str] | None,
    ) -> str:
        directions = self._join_values(direction_titles, "、", "所选创新方向")
        breakthroughs = self._join_values(
            breakthrough_labels,
            "、",
            definition.category,
        )
        canvas_keywords = self._join_values(
            definition.canvas_keywords[:2],
            "、",
            definition.category,
        )
        return (
            f"围绕{directions}，以{definition.name}切入{canvas_keywords}，"
            f"优先解决{breakthroughs}中的高频经营问题。"
        )

    def _build_benefits(self, definition: ScenarioDefinition) -> list[ScenarioBenefit]:
        _, _, benefit_canvas = self._resolve_canvas_meta(definition)
        goals = definition.goal_keywords[:2] or [definition.category]
        benefits = [
            ScenarioBenefit(text=_benefit_text(goal), canvas=benefit_canvas)
            for goal in goals
        ]
        if len(benefits) < 2:
            benefits.append(
                ScenarioBenefit(
                    text=f"预计可减少{definition.category}环节反复沟通",
                    canvas=benefit_canvas,
                )
            )
        return benefits[:3]

    def _build_resources(self, definition: ScenarioDefinition) -> list[ScenarioResource]:
        resources = [
            ScenarioResource(type="data", label="数据基础", text=requirement)
            for requirement in definition.data_requirements[:2]
        ]
        resources.append(
            ScenarioResource(
                type="org",
                label="组织准备",
                text=f"由{definition.category}负责人牵头确认试点口径",
            )
        )
        return resources[:3]

    def _join_values(
        self,
        values: list[str] | None,
        separator: str,
        fallback: str,
    ) -> str:
        if not values:
            return fallback

        cleaned = [value.strip() for value in values if value and value.strip()]
        return separator.join(cleaned[:3]) if cleaned else fallback

    def _normalize_text(self, text: str | None) -> str:
        if not text:
            return ""

        return re.sub(r"[^\w\u4e00-\u9fff]+", "", text).lower()
