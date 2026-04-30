from app.schemas.assessment import CanvasDiagnosisResult
from app.schemas.competitiveness import (
    COMPETITIVENESS_KNOWLEDGE,
    CompetitivenessResult,
    CoreAdvantage,
    DeliveryStrategy,
    PointToLineConnection,
    VPReconstruction,
)
from app.schemas.breakthrough import ELEMENT_KEY_TO_TITLE
from app.schemas.direction import DirectionSuggestion


class CompetitivenessAnalyzer:
    def analyze(
        self,
        canvas_diagnosis: CanvasDiagnosisResult,
        breakthrough_keys: list[str],
        selected_directions: list[DirectionSuggestion],
    ) -> CompetitivenessResult:
        vp = self._build_vp_reconstruction(canvas_diagnosis, breakthrough_keys, selected_directions)
        connections = self._build_connections(selected_directions)
        advantages = self._build_advantages(breakthrough_keys, selected_directions)
        strategy = self._build_delivery_strategy(canvas_diagnosis, breakthrough_keys)
        narrative = self._build_narrative(vp, connections, advantages)

        return CompetitivenessResult(
            generation_mode="rule_based",
            vp_reconstruction=vp,
            connections=connections,
            advantages=advantages,
            delivery_strategy=strategy,
            overall_narrative=narrative,
        )

    def _build_vp_reconstruction(
        self,
        canvas: CanvasDiagnosisResult,
        breakthrough_keys: list[str],
        directions: list[DirectionSuggestion],
    ) -> VPReconstruction:
        current_vp_block = None
        for block in canvas.canvas.blocks:
            if block.key == "value_propositions":
                current_vp_block = block
                break

        current_vp = (
            current_vp_block.current_state
            if current_vp_block
            else "当前价值主张数据不完整"
        )

        enhancement_templates = COMPETITIVENESS_KNOWLEDGE["vp_enhancement_templates"]
        enhancement_parts: list[str] = []
        for key in breakthrough_keys:
            template = enhancement_templates.get(key)
            if template:
                enhancement_parts.append(template)

        direction_titles = [d.title for d in directions[:4]]
        enhanced_vp = (
            f"在现有价值基础上，通过{'、'.join(enhancement_parts[:3] or ['技术与管理创新'])}，"
            f"围绕{'、'.join(direction_titles[:3] or ['核心业务方向'])}构建差异化竞争力，"
            f"实现从产品能力到客户价值的系统性升级。"
        )

        differentiation_points = [f"{p} → 形成可持续的竞争壁垒" for p in enhancement_parts[:3]]
        if not differentiation_points:
            differentiation_points = ["通过选定的突破要素构建差异化定位"]

        bl = canvas.canvas.blocks
        weakest_titles = [
            bl[i].title if i < len(bl) else ""
            for i, _ in enumerate(canvas.weakest_blocks[:2])
        ]

        customer_value_shift = (
            f"从'{current_vp[:40]}...'的价值叙事，升级为以"
            f"'{enhancement_parts[0] if enhancement_parts else '客户价值'}'"
            f"为核心的差异化定位，通过修补'{'、'.join(weakest_titles or ['关键薄弱环节'])}'"
            f"等薄弱环节，建立不可替代的客户价值感知。"
        )

        return VPReconstruction(
            current_vp=current_vp,
            enhanced_vp=enhanced_vp,
            differentiation_points=differentiation_points,
            customer_value_shift=customer_value_shift,
        )

    def _build_connections(
        self,
        directions: list[DirectionSuggestion],
    ) -> list[PointToLineConnection]:
        category_to_line = COMPETITIVENESS_KNOWLEDGE["category_to_line"]
        line_templates = COMPETITIVENESS_KNOWLEDGE["line_templates"]

        line_map: dict[str, list[DirectionSuggestion]] = {}
        for d in directions:
            for category in d.related_scenario_categories:
                matched_lines = category_to_line.get(category, [])
                for line_name in matched_lines:
                    if line_name not in line_map:
                        line_map[line_name] = []
                    if d not in line_map[line_name]:
                        line_map[line_name].append(d)

        connections: list[PointToLineConnection] = []
        for line_name, line_directions in line_map.items():
            template = line_templates.get(line_name, {})
            point_titles = [d.title for d in line_directions]
            joined = "、".join(point_titles[:4])
            narrative = (
                f"将{'、'.join([d.title for d in line_directions[:2]])}等方向串联为"
                f"「{line_name}」，{template.get('description', '形成系统性竞争优势')}。"
                f"这不仅是单点提效，而是通过流程串联实现{template.get('impact', '整体能力升级')}。"
            )
            connections.append(
                PointToLineConnection(
                    line_name=line_name,
                    point_ids=[d.direction_id for d in line_directions],
                    point_titles=point_titles,
                    strategic_narrative=narrative,
                    competitive_impact=template.get("impact", "提升整体竞争优势"),
                    key_metrics=list(template.get("metrics", [])),
                )
            )

        if not connections:
            connections.append(
                PointToLineConnection(
                    line_name="综合竞争力线",
                    point_ids=[],
                    point_titles=[],
                    strategic_narrative="当前方向尚未形成明确的线级竞争力，建议进一步聚焦方向选择。",
                    competitive_impact="待方向聚焦后评估",
                    key_metrics=["待补充"],
                )
            )

        return connections

    def _build_advantages(
        self,
        breakthrough_keys: list[str],
        directions: list[DirectionSuggestion],
    ) -> list[CoreAdvantage]:
        advantages: list[CoreAdvantage] = []

        for key in breakthrough_keys:
            title = ELEMENT_KEY_TO_TITLE.get(key, key)
            matching_dirs = [d for d in directions if d.element_key == key]
            if matching_dirs:
                advantages.append(
                    CoreAdvantage(
                        advantage_name=f"差异化{title}优势",
                        source_elements=[title],
                        description=(
                            f"围绕「{title}」这一突破要素，"
                            f"通过{'、'.join([d.title for d in matching_dirs[:2]])}"
                            f"等方向构建独特能力体系，在当前行业竞争格局中形成差异化壁垒。"
                        ),
                        barrier_level="高" if len(matching_dirs) >= 2 else "中",
                    )
                )

        if directions:
            advantages.append(
                CoreAdvantage(
                    advantage_name="系统性创新组合优势",
                    source_elements=[ELEMENT_KEY_TO_TITLE.get(k, k) for k in breakthrough_keys],
                    description=(
                        f"将{len(breakthrough_keys)}个突破要素与{len(directions)}个创新方向"
                        f"组合为系统性竞争力方案，竞争对手难以单点复制。"
                    ),
                    barrier_level="高",
                )
            )

        if not advantages:
            advantages.append(
                CoreAdvantage(
                    advantage_name="基础能力优势",
                    source_elements=["待补充"],
                    description="通过已有业务基础构建先发优势，建议尽快完成方向聚焦以深化壁垒。",
                    barrier_level="低",
                )
            )

        return advantages

    def _build_delivery_strategy(
        self,
        canvas: CanvasDiagnosisResult,
        breakthrough_keys: list[str],
    ) -> DeliveryStrategy:
        breakthrough_labels = [ELEMENT_KEY_TO_TITLE.get(k, k) for k in breakthrough_keys]
        joined = "、".join(breakthrough_labels[:2]) if breakthrough_labels else "核心要素"

        weakest = canvas.weakest_blocks[:2]
        weakest_str = "、".join(weakest) if weakest else "关键薄弱环节"

        return DeliveryStrategy(
            phase_1_quick_win=(
                f"优先围绕「{joined}」实施 1-2 个可快速验证的方向，"
                f"在 30 天内产出可量化的业务改进数据，建立组织信心。"
            ),
            phase_2_scale=(
                f"将试点经验扩展至相邻流程和团队，重点修补「{weakest_str}」"
                f"等薄弱环节，在 60 天内形成可复制的竞争力模板。"
            ),
            phase_3_moat=(
                f"将已验证的差异化能力沉淀为组织标准和系统能力，"
                f"在 90-120 天内形成竞争对手难以短期复制的系统性优势。"
            ),
            key_risks=[
                f"如果「{joined}」方向的数据基础不足，试点周期可能延长 2-4 周。",
                f"跨部门协同机制不完善会直接影响「{weakest_str}」的改进速度。",
                "组织惯性可能导致新方法被旧流程稀释，需要明确负责人和决策权限。",
            ],
        )

    def _build_narrative(
        self,
        vp: VPReconstruction,
        connections: list[PointToLineConnection],
        advantages: list[CoreAdvantage],
    ) -> str:
        line_names = [c.line_name for c in connections[:3]]
        joined_lines = "、".join(line_names) if line_names else "多维度竞争力"

        high_barrier_advantages = [a.advantage_name for a in advantages if a.barrier_level == "高"]
        joined_advantages = "、".join(high_barrier_advantages[:3]) if high_barrier_advantages else "核心优势"

        return (
            f"本评估的核心结论是：企业应围绕「{vp.enhanced_vp[:50]}...」这一增强型价值主张，"
            f"通过构建「{joined_lines}」等系统性竞争力线路，"
            f"重点培育「{joined_advantages}」。"
            f"这些能力组合不是单点技术工具的叠加，而是从客户价值感知、"
            f"运营效率和商业模式三个维度形成的不可替代的综合优势。"
        )
