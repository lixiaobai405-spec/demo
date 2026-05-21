"""Prompt templates for Top 3 AI scenario narrative packaging."""

from __future__ import annotations

from typing import Iterable

from app.models.assessment import Assessment
from app.schemas.assessment import (
    CanvasDiagnosisResult,
    CompanyProfileResult,
    ScenarioRecommendationItem,
)
from app.schemas.direction import DirectionSuggestion


class ScenarioWriterPrompt:
    """Build prompts for LLM-based Top 3 scenario narrative polishing."""

    @staticmethod
    def build_system_prompt() -> str:
        return """
你是一位面向企业高管的商业创新顾问，负责将已经选出的 Top 3 AI 推荐场景，改写成更清晰、更有管理语言的业务表达。

你的职责是“包装既有结论”，不是重新做推荐，更不是补充不存在的事实。

硬性边界：
1. 只能使用输入中已经提供的企业信息、画布诊断、突破要素、创新方向和场景草稿。
2. 不得编造任何新的公司事实、行业事实、客户事实、竞争事实、数据来源或业务结果。
3. 不得自行补充 ROI 数字、比例、时长、市场规模等量化数据；除非这些数字已经在输入中出现。
4. 不得输出技术黑话，如模型、API、向量数据库、Prompt Engineering、Agent 编排等。
5. 必须使用管理层能直接理解的业务语言，强调业务动作、管理含义、组织准备和经营价值。
6. 三个场景之间必须写出明确差异，不能只是同一段话换标题。
7. 不得新增新的突破要素标签；只能引用输入中已给出的突破要素。
8. 不得修改 scenario_id、name、category、排序、评分、象限等既有结果。

字段要求：
- summary：写成“场景描述 + 战略定位”，说明它为什么适合这家企业、会嵌入哪段经营动作。80-140 字。
- canvas_elements：写成“对应突破要素 + 对应创新方向 + 战略价值”，强调为什么这件事值得优先做。
- expected_effects：写成“预期收益”，只能使用输入中已有的定性结论，避免空话，例如不要只写“提升效率”“优化流程”。
- core_data_requirements：写成“资源准备”，只写当前已知需要准备的数据、流程、组织或协同条件。

如果输入信息不足：
- 允许保留原草稿中已经出现的表述；
- 不允许为了写满而新增事实；
- 可以使用“基于现有信息，可先…”这样的保守表达。

只输出合法 JSON，不要输出任何额外说明。输出格式：
{
  "scenarios": [
    {
      "scenario_id": "保持与输入一致",
      "summary": "string",
      "canvas_elements": "string",
      "expected_effects": "string",
      "core_data_requirements": "string"
    }
  ]
}
""".strip()

    @staticmethod
    def build_user_prompt(
        assessment: Assessment,
        profile: CompanyProfileResult | None,
        canvas: CanvasDiagnosisResult,
        breakthrough_labels: list[str],
        selected_directions: list[DirectionSuggestion],
        scenarios: list[ScenarioRecommendationItem],
    ) -> str:
        sections = [
            "## 企业已知输入",
            ScenarioWriterPrompt._format_assessment(assessment),
            "\n## 企业画像（已生成）",
            ScenarioWriterPrompt._format_profile(profile),
            "\n## 商业画布诊断（已生成）",
            ScenarioWriterPrompt._format_canvas(canvas),
            "\n## 已确认突破要素",
            ScenarioWriterPrompt._format_breakthroughs(breakthrough_labels),
            "\n## 已确认创新方向",
            ScenarioWriterPrompt._format_directions(selected_directions),
            "\n## 当前 Top 3 场景草稿（只允许在此基础上改写，不可换题）",
            ScenarioWriterPrompt._format_scenarios(scenarios),
            "\n## 改写任务",
            "\n".join(
                [
                    "请严格基于以上内容，对 3 个场景分别改写四个字段：summary、canvas_elements、expected_effects、core_data_requirements。",
                    "三个场景都要保留原有 scenario_id，并且一一对应返回。",
                    "必须让每个场景显式对应已确认的突破要素和创新方向。",
                    "如果某个场景的草稿里没有足够信息，请做保守收敛，不要补新事实。",
                ]
            ),
        ]
        return "\n".join(sections)

    @staticmethod
    def _format_assessment(assessment: Assessment) -> str:
        lines = [
            f"- 企业名称：{assessment.company_name or '未提供'}",
            f"- 所属行业：{assessment.industry or '未提供'}",
            f"- 企业规模：{assessment.company_size or '未提供'}",
        ]
        optional_pairs = [
            ("区域", assessment.region),
            ("年营收范围", assessment.annual_revenue_range),
            ("核心产品/服务", assessment.core_products),
            ("目标客户", assessment.target_customers),
            ("当前挑战", assessment.current_challenges),
            ("AI 目标", assessment.ai_goals),
            ("可用数据", assessment.available_data),
            ("补充说明", assessment.notes),
        ]
        for label, value in optional_pairs:
            if value:
                lines.append(f"- {label}：{value}")
        return "\n".join(lines)

    @staticmethod
    def _format_profile(profile: CompanyProfileResult | None) -> str:
        if profile is None:
            return "暂无企业画像。"

        lines = [
            f"- 企业概览：{profile.company_summary or '未提供'}",
            f"- 价值主张：{profile.value_proposition or '未提供'}",
            f"- 客户与市场：{profile.customer_and_market or '未提供'}",
            f"- 运营与资源：{profile.operations_and_resources or '未提供'}",
            f"- 数字化与 AI 准备度：{profile.digital_and_ai_readiness or '未提供'}",
        ]
        if profile.key_challenges:
            lines.append(
                f"- 关键挑战：{ScenarioWriterPrompt._join(profile.key_challenges)}"
            )
        if profile.priority_ai_directions:
            lines.append(
                f"- 优先 AI 方向：{ScenarioWriterPrompt._join(profile.priority_ai_directions)}"
            )
        return "\n".join(lines)

    @staticmethod
    def _format_canvas(canvas: CanvasDiagnosisResult) -> str:
        lines = [
            f"- 总体评分：{canvas.overall_score}",
            f"- 最薄弱模块：{ScenarioWriterPrompt._join(canvas.weakest_blocks, '暂无')}",
            f"- 建议聚焦：{ScenarioWriterPrompt._join(canvas.recommended_focus, '暂无')}",
            f"- 整体摘要：{canvas.canvas.overall_summary or '未提供'}",
        ]
        for block in canvas.canvas.blocks:
            lines.append(
                "\n".join(
                    [
                        f"- 模块：{block.title}",
                        f"  当前状态：{block.current_state or '未提供'}",
                        f"  诊断：{block.diagnosis or '未提供'}",
                        f"  AI 机会：{block.ai_opportunity or '未提供'}",
                    ]
                )
            )
        return "\n".join(lines)

    @staticmethod
    def _format_breakthroughs(labels: list[str]) -> str:
        if not labels:
            return "暂无已确认突破要素。"
        return f"- 已确认突破要素：{ScenarioWriterPrompt._join(labels)}"

    @staticmethod
    def _format_directions(selected_directions: list[DirectionSuggestion]) -> str:
        if not selected_directions:
            return "暂无已确认创新方向。"
        lines: list[str] = []
        for item in selected_directions:
            lines.append(f"- 方向标题：{item.title}")
            lines.append(f"  描述：{item.description or '未提供'}")
            lines.append(f"  预期影响：{item.expected_impact or '未提供'}")
            if item.data_needed:
                lines.append(f"  所需数据：{ScenarioWriterPrompt._join(item.data_needed)}")
            if item.related_scenario_categories:
                lines.append(
                    f"  关联场景类别：{ScenarioWriterPrompt._join(item.related_scenario_categories)}"
                )
        return "\n".join(lines)

    @staticmethod
    def _format_scenarios(scenarios: list[ScenarioRecommendationItem]) -> str:
        lines: list[str] = []
        for index, item in enumerate(scenarios, start=1):
            lines.append(f"### 场景 {index}")
            lines.append(f"- scenario_id：{item.scenario_id}")
            lines.append(f"- 场景名称：{item.name}")
            lines.append(f"- 场景类别：{item.category}")
            if item.priority_quadrant:
                lines.append(f"- 象限：{item.priority_quadrant}")
            if item.priority_recommendation:
                lines.append(f"- 推荐说明：{item.priority_recommendation}")
            lines.append(f"- 当前草稿 summary：{item.summary or '未提供'}")
            lines.append(
                f"- 当前草稿 canvas_elements：{item.canvas_elements or '未提供'}"
            )
            lines.append(
                f"- 当前草稿 expected_effects：{item.expected_effects or '未提供'}"
            )
            lines.append(
                "- 当前草稿 core_data_requirements："
                f"{item.core_data_requirements or '未提供'}"
            )
        return "\n".join(lines)

    @staticmethod
    def _join(values: Iterable[str], fallback: str = "暂无") -> str:
        cleaned = [value.strip() for value in values if value and value.strip()]
        return "、".join(cleaned) if cleaned else fallback
