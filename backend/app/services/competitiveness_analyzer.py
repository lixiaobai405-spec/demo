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
            f"从'{current_vp}'的价值叙事，升级为以"
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
            first_two = [d.title for d in line_directions[:2]]
            pts_joined = "、".join(point_titles[:3])
            connections.append(
                PointToLineConnection(
                    line_name=line_name,
                    point_ids=[d.direction_id for d in line_directions],
                    point_titles=point_titles,
                    strategic_narrative=narrative,
                    competitive_impact=template.get("impact", "提升整体竞争优势"),
                    key_metrics=list(template.get("metrics", [])),
                    linkage_logic=(
                        f"AI不再只是辅助工具，而是连接{pts_joined}的'神经中枢'——"
                        f"实时汇聚各环节数据，驱动从感知、决策到执行的闭环。"
                        f"例如，当{point_titles[0] if point_titles else '前端'}的异常信号被捕捉后，"
                        f"系统自动联动{'、'.join(point_titles[1:3]) if len(point_titles) > 1 else '后端'}"
                        f"进行调整，人工只需审核关键节点。"
                    ),
                    competitive_moat=(
                        f"「{line_name}」不是单点工具的堆砌，而是将{pts_joined}"
                        f"编织为一条AI驱动的智能流水线。这种串联一旦跑通，"
                        f"数据和算法的飞轮效应会持续拉大与跟随者的差距——"
                        f"每多跑一轮，模型就更精准、响应就更快、成本就更低，"
                        f"形成'越用越强、越强越难追'的结构性壁垒。"
                    ),
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
                    linkage_logic="",
                    competitive_moat="",
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
                dir_titles = [d.title for d in matching_dirs[:3]]
                joined = "、".join(dir_titles)
                advantages.append(
                    CoreAdvantage(
                        advantage_name=f"差异化{title}优势",
                        source_elements=[title],
                        description=(
                            f"以「{title}」为支点，通过AI将{joined}"
                            f"等方向的数据采集、分析决策和执行反馈连为一体，"
                            f"形成'数据驱动感知—算法辅助决策—自动化执行—效果回流优化'的闭环。"
                            f"竞争对手若仅模仿其中单一环节，无法复制端到端的系统性效率提升。"
                        ),
                        barrier_level="高" if len(matching_dirs) >= 2 else "中",
                    )
                )

        if directions:
            breakthrough_titles = [ELEMENT_KEY_TO_TITLE.get(k, k) for k in breakthrough_keys]
            advantages.append(
                CoreAdvantage(
                    advantage_name="系统性创新组合优势",
                    source_elements=breakthrough_titles,
                    description=(
                        f"将{'、'.join(breakthrough_titles[:3])}等突破要素通过"
                        f"{len(directions)}个AI创新方向有机串联，构成'要素×方向'的矩阵化能力体系。"
                        f"每一对组合都形成数据和算法的交叉强化，使护城河不是单点优势的叠加，"
                        f"而是多维能力的乘数效应——竞争对手即使突破1-2个点，也难以同步攻克整个系统。"
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
                f"产出可量化的业务改进数据，建立组织信心。"
            ),
            phase_2_scale=(
                f"将试点经验扩展至相邻流程和团队，重点修补「{weakest_str}」"
                f"等薄弱环节，形成可复制的竞争力模板。"
            ),
            phase_3_moat=(
                f"将已验证的差异化能力沉淀为组织标准和系统能力，"
                f"形成竞争对手难以短期复制的系统性优势。"
            ),
            key_risks=[
                f"如果「{joined}」方向的数据基础不足，试点周期可能延长。",
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
            f"本评估的核心结论是：企业应围绕「{vp.enhanced_vp}」这一增强型价值主张，"
            f"通过构建「{joined_lines}」等系统性竞争力线路，"
            f"重点培育「{joined_advantages}」。"
            f"这些能力组合不是单点技术工具的叠加，而是从客户价值感知、"
            f"运营效率和商业模式三个维度形成的不可替代的综合优势。"
        )
