from app.models.assessment import Assessment
from app.schemas.assessment import (
    CanvasDiagnosisResult,
    CaseRecommendationResult,
    CompanyProfileResult,
    ReportActionItem,
    ReportCardData,
    ReportData,
    ReportRoadmapStage,
    ReportSectionData,
    ReportTableData,
    ScenarioRecommendationResult,
)
from app.schemas.breakthrough import ELEMENT_KEY_TO_TITLE


class ReportBuilder:
    def build(
        self,
        assessment: Assessment,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
        case_recommendation: CaseRecommendationResult | None,
        breakthrough_keys: list[str] | None = None,
        direction_labels: list[str] | None = None,
        competitiveness_result = None,
        enrichment_result = None,
        endgame_result = None,
    ) -> ReportData:
        ai_readiness_score = self._calculate_ai_readiness_score(
            profile=profile,
            canvas_diagnosis=canvas_diagnosis,
            scenario_recommendation=scenario_recommendation,
        )
        roadmap = self._build_roadmap(canvas_diagnosis, scenario_recommendation)
        action_plan = self._build_action_plan(canvas_diagnosis, scenario_recommendation)
        breakthrough_labels = self._resolve_breakthrough_labels(breakthrough_keys or [])
        direction_labels = direction_labels or []
        canvas_blocks = canvas_diagnosis.canvas.blocks

        sections = [
            self._build_company_profile_section(profile),
            self._build_canvas_section(canvas_diagnosis),
            self._build_breakthrough_section(breakthrough_labels, canvas_blocks),
            self._build_direction_section(direction_labels),
            self._build_ai_readiness_section(ai_readiness_score, profile, canvas_diagnosis),
            self._build_priority_scenarios_section(scenario_recommendation),
            self._build_scenario_planning_section(scenario_recommendation),
            self._build_competitiveness_section(profile, canvas_diagnosis, scenario_recommendation, competitiveness_result),
            self._build_cases_section(case_recommendation),
            self._build_roadmap_section(roadmap),
            self._build_action_plan_section(action_plan),
            self._build_risk_section(profile, canvas_diagnosis, scenario_recommendation),
            self._build_instructor_section(profile, scenario_recommendation, enrichment_result),
            self._build_endgame_section(endgame_result, profile, canvas_diagnosis),
        ]

        return ReportData(
            title=f"{assessment.company_name} AI 商业创新建议报告",
            subtitle=f"{assessment.industry} | {assessment.region} | 模板化管理层阅读版",
            company_name=assessment.company_name,
            industry=assessment.industry,
            company_size=assessment.company_size,
            region=assessment.region,
            annual_revenue_range=assessment.annual_revenue_range,
            ai_readiness_score=ai_readiness_score,
            ai_readiness_summary=self._build_ai_readiness_summary(
                ai_readiness_score,
                profile,
                canvas_diagnosis,
            ),
            generated_with="template",
            sections=sections,
        )

    def _calculate_ai_readiness_score(
        self,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> int:
        score = canvas_diagnosis.overall_score
        score -= min(18, len(profile.missing_information) * 3)
        score += min(8, len(profile.priority_ai_directions) * 2)
        if scenario_recommendation.top_scenarios:
            score += 5
        if "待补充" in profile.digital_and_ai_readiness:
            score -= 5
        return max(35, min(95, score))

    def _build_ai_readiness_summary(
        self,
        score: int,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
    ) -> str:
        weakest_blocks = self._join_or_todo(canvas_diagnosis.weakest_blocks[:2], "、")
        if score >= 75:
            return (
                "企业已经具备相对明确的试点条件，可以围绕当前高优先级场景直接推进业务试点，"
                f"同时优先修补 {weakest_blocks} 相关的管理与协同短板。"
            )
        if score >= 60:
            return (
                "企业具备初步 AI 推进基础，但仍需先统一关键数据口径、明确责任人和验收标准，"
                f"尤其要先补齐 {weakest_blocks} 对应的流程与数据基础。"
            )
        return (
            "企业当前更适合先做数据盘点、流程梳理和跨部门协同机制建设，再选择低风险、可量化的小范围试点，"
            f"优先从 {weakest_blocks} 对应问题切入。"
        )

    def _build_company_profile_section(
        self,
        profile: CompanyProfileResult,
    ) -> ReportSectionData:
        return ReportSectionData(
            key="company_profile",
            title="企业基本画像",
            content=profile.company_summary,
            cards=[
                ReportCardData(title="价值主张", content=profile.value_proposition),
                ReportCardData(title="客户与市场", content=profile.customer_and_market),
                ReportCardData(title="运营与资源", content=profile.operations_and_resources),
                ReportCardData(
                    title="数字化与 AI 准备度",
                    content=profile.digital_and_ai_readiness,
                ),
            ],
            bullets=[
                f"关键挑战：{self._join_or_todo(profile.key_challenges)}",
                f"优先 AI 方向：{self._join_or_todo(profile.priority_ai_directions)}",
                f"待补充信息：{self._join_or_todo(profile.missing_information)}",
            ],
        )

    def _build_canvas_section(
        self,
        canvas_diagnosis: CanvasDiagnosisResult,
    ) -> ReportSectionData:
        return ReportSectionData(
            key="canvas_diagnosis",
            title="当前商业模式画布诊断",
            content=canvas_diagnosis.canvas.overall_summary,
            bullets=[
                f"整体评分：{canvas_diagnosis.overall_score}",
                f"薄弱模块：{self._join_or_todo(canvas_diagnosis.weakest_blocks)}",
                f"建议优先动作：{self._join_or_todo(canvas_diagnosis.recommended_focus)}",
            ],
            cards=[
                ReportCardData(
                    title=block.title,
                    subtitle="Business Model Canvas",
                    content=block.current_state,
                    highlight=f"AI 机会：{block.ai_opportunity}",
                    bullets=[
                        f"诊断：{block.diagnosis}",
                        f"待补充：{block.missing_information}",
                    ],
                )
                for block in canvas_diagnosis.canvas.blocks
            ],
        )

    def _build_ai_readiness_section(
        self,
        score: int,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
    ) -> ReportSectionData:
        return ReportSectionData(
            key="ai_readiness",
            title="AI 成熟度评估",
            content=self._build_ai_readiness_summary(score, profile, canvas_diagnosis),
            bullets=[
                f"AI 就绪度评分：{score}",
                f"数字化与 AI 准备度判断：{profile.digital_and_ai_readiness}",
                f"当前优先补齐项：{self._join_or_todo(profile.missing_information[:3])}",
            ],
            note="该评分仅作为管理层判断和排序参考，不代表财务回报承诺，也不替代正式立项评审。",
        )

    def _build_priority_scenarios_section(
        self,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> ReportSectionData:
        table = ReportTableData(
            columns=["推荐场景", "类别", "评分", "推荐理由", "数据需求"],
            rows=[
                [
                    item.name,
                    item.category,
                    str(item.score),
                    self._join_or_todo(item.reasons),
                    self._join_or_todo(item.data_requirements),
                ]
                for item in scenario_recommendation.top_scenarios
            ],
        )
        return ReportSectionData(
            key="priority_scenarios",
            title="高优先级 AI 提效场景",
            content=(
                "以下场景基于企业问卷、商业画布诊断和规则评分结果生成，"
                "适合作为当前阶段优先验证的 AI 提效切入口。"
            ),
            table=table,
        )

    def _build_scenario_planning_section(
        self,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> ReportSectionData:
        return ReportSectionData(
            key="scenario_planning",
            title="推荐场景详细规划",
            content=(
                "建议把推荐场景拆成可验证、可复盘的单点试点，先在一个业务单元内跑通，"
                "再逐步复制到相邻流程，降低组织推进阻力。"
            ),
            cards=[
                ReportCardData(
                    title=item.name,
                    subtitle=item.category,
                    content=item.summary,
                    highlight=f"优先级评分：{item.score}",
                    bullets=[
                        f"推荐理由：{self._join_or_todo(item.reasons)}",
                        f"数据需求：{self._join_or_todo(item.data_requirements)}",
                        "试点建议：先定义成功标准、责任人、验收频次和异常兜底机制。",
                    ],
                )
                for item in scenario_recommendation.top_scenarios
            ],
        )

    def _build_competitiveness_section(
        self,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
        competitiveness_result=None,
    ) -> ReportSectionData:
        if competitiveness_result is not None:
            cr = competitiveness_result
            vp = cr.vp_reconstruction
            connections_text = "；".join(
                [f"{c.line_name}（{c.competitive_impact}）" for c in cr.connections[:3]]
            ) if cr.connections else ""
            advantages_text = "；".join(
                [f"{a.advantage_name}（壁垒{a.barrier_level}）" for a in cr.advantages[:3]]
            ) if cr.advantages else ""

            cards = []
            for conn in cr.connections[:3]:
                cards.append(
                    ReportCardData(
                        title=conn.line_name,
                        subtitle="到线串联",
                        content=conn.strategic_narrative,
                        highlight=f"竞争影响：{conn.competitive_impact}",
                        bullets=[f"核心指标：{', '.join(conn.key_metrics[:3])}"],
                    )
                )

            return ReportSectionData(
                key="competitiveness",
                title="差异化竞争力设计",
                content=cr.overall_narrative,
                bullets=[
                    f"增强型价值主张：{vp.enhanced_vp[:100]}...",
                    f"客户价值转移：{vp.customer_value_shift[:100]}...",
                    f"串联竞争力线：{connections_text or '待补充'}",
                    f"核心优势：{advantages_text or '待补充'}",
                ],
                cards=cards if cards else None,
                note=(
                    cr.delivery_strategy.phase_1_quick_win[:120] + "..."
                    if cr.delivery_strategy else None
                ),
            )

        top_scenarios = [item.name for item in scenario_recommendation.top_scenarios[:2]]
        weakest_blocks = canvas_diagnosis.weakest_blocks[:2]
        return ReportSectionData(
            key="competitiveness",
            title="差异化竞争力设计",
            content=(
                f"建议不要把 AI 仅当作内部降本工具，而要围绕“{profile.value_proposition}”重新组织客户响应速度、"
                "知识复用效率和跨部门协同能力。优先把 "
                f"{self._join_or_todo(top_scenarios)} 做成客户可感知的改进点，同时修补 "
                f"{self._join_or_todo(weakest_blocks)} 对应的商业模式薄弱环节，让 AI 成为竞争力放大器。"
            ),
            bullets=[
                "把高频重复工作转为标准化能力，缩短业务响应周期。",
                "把知识和数据沉淀为组织资产，减少对个人经验的依赖。",
                "把试点经验映射到客户价值和经营指标，形成持续扩展基础。",
            ],
        )

    def _build_cases_section(
        self,
        case_recommendation: CaseRecommendationResult | None,
    ) -> ReportSectionData:
        if not case_recommendation or not case_recommendation.top_cases:
            return ReportSectionData(
                key="cases",
                title="参考案例与启示",
                content=(
                    "当前未匹配到足够贴合的匿名行业参考案例。下一阶段可以接入案例检索增强能力。"
                    "本报告在案例部分统一标记为“待补充”，避免编造真实客户名称或真实 ROI。"
                ),
                bullets=["待补充：后续可在报告生成端接入案例检索与 RAG。"],
            )

        return ReportSectionData(
            key="cases",
            title="参考案例与启示",
            content=(
                "以下内容均为匿名行业参考案例，仅用于帮助管理层理解类似场景的落地方式，"
                "不代表真实客户名称，也不构成真实 ROI 承诺。"
            ),
            cards=[
                ReportCardData(
                    title=item.title,
                    subtitle=item.industry,
                    content=item.summary,
                    highlight=f"匹配分数：{item.fit_score}",
                    bullets=[
                        f"匹配理由：{self._join_or_todo(item.match_reasons)}",
                        f"参考做法：{self._join_or_todo(item.reference_points)}",
                        f"数据基础：{self._join_or_todo(item.data_foundation)}",
                        f"注意事项：{self._join_or_todo(item.cautions)}",
                    ],
                )
                for item in case_recommendation.top_cases
            ],
        )

    def _build_roadmap_section(
        self,
        roadmap: list[ReportRoadmapStage],
    ) -> ReportSectionData:
        return ReportSectionData(
            key="roadmap",
            title="三阶段 AI 创新路线图",
            content="建议按“短期单点提效 -> 中期差异化竞争力 -> 长期生态与增长路径”的顺序推进。",
            cards=[
                ReportCardData(
                    title=stage.stage_name,
                    subtitle=stage.time_horizon,
                    content=stage.strategic_focus,
                    bullets=[
                        f"优先动作：{self._join_or_todo(stage.priority_actions)}",
                        f"阶段产出：{self._join_or_todo(stage.expected_outputs)}",
                    ],
                )
                for stage in roadmap
            ],
        )

    def _build_action_plan_section(
        self,
        action_plan: list[ReportActionItem],
    ) -> ReportSectionData:
        return ReportSectionData(
            key="action_plan",
            title="90 天行动计划",
            content="建议把前 90 天定义为“试点验证期”，先把目标、数据、责任人和复盘机制建立起来。",
            table=ReportTableData(
                columns=["周期", "行动项", "建议负责人", "交付物"],
                rows=[
                    [item.period, item.action, item.owner_suggestion, item.deliverable]
                    for item in action_plan
                ],
            ),
        )

    def _build_risk_section(
        self,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> ReportSectionData:
        bullets = [
            "如果关键业务数据口径不统一，报告中的建议难以稳定落地，需先统一口径。",
            "如果试点场景过多，组织协同成本会快速上升，建议先聚焦 1 到 2 个场景。",
            "如果没有业务负责人参与验收，AI 项目容易停留在演示层，无法进入经营闭环。",
        ]

        for item in profile.missing_information[:2]:
            bullets.append(f"待补充信息风险：{item}")

        if canvas_diagnosis.weakest_blocks:
            bullets.append(
                f"商业模式薄弱点集中在 {self._join_or_todo(canvas_diagnosis.weakest_blocks[:3])}，"
                "会直接影响推荐场景的落地速度。"
            )

        if scenario_recommendation.top_scenarios:
            top_scenario = scenario_recommendation.top_scenarios[0]
            bullets.append(
                f"首选场景“{top_scenario.name}”依赖的数据基础包括 {self._join_or_todo(top_scenario.data_requirements)}。"
            )

        return ReportSectionData(
            key="risks",
            title="风险与阻力",
            content="以下风险不是否定 AI 推进，而是帮助管理层提前设定边界、节奏和验收机制。",
            bullets=bullets[:7],
        )

    def _build_instructor_section(
        self,
        profile: CompanyProfileResult,
        scenario_recommendation: ScenarioRecommendationResult,
        enrichment_result=None,
    ) -> ReportSectionData:
        if enrichment_result is not None:
            ic = enrichment_result.instructor_comment
            return ReportSectionData(
                key="instructor_comments",
                title="讲师点评区",
                content=ic.overall_assessment,
                bullets=[
                    f"优势：{p}" for p in ic.strength_points[:3]
                ] + [
                    f"风险：{r}" for r in ic.risk_warnings[:3]
                ],
                note=(
                    f"推荐阅读：{'、'.join(ic.recommended_reading[:3]) or '待补充'}"
                ),
            )

        top_name = (
            scenario_recommendation.top_scenarios[0].name
            if scenario_recommendation.top_scenarios
            else "待补充"
        )
        return ReportSectionData(
            key="instructor_comments",
            title="讲师点评区",
            content=(
                "讲师点评建议：当前企业更适合采用\u201c先验证一个高频试点，再把经验复制到相邻流程\u201d的推进方式。"
                f"优先围绕 {top_name} 这类能较快体现业务价值的场景切入，同时关注 "
                f"{profile.digital_and_ai_readiness} 所暴露出的组织准备度问题。"
            ),
            note="该区域适合作为后续人工点评、讲师批注、高层会议纪要或培训反馈的补充位置。",
        )

    def _build_endgame_section(
        self,
        endgame_result,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
    ) -> ReportSectionData:
        if endgame_result is None:
            return ReportSectionData(
                key="endgame",
                title="商业终局设计",
                content="该评估尚未生成商业终局分析。建议在完成竞争力和场景分析后，生成完整的商业终局设计方案。",
                note="商业终局是 V2 面阶段的核心交付物，建议在条件成熟时通过 /endgame/generate 端点生成。",
            )

        er = endgame_result
        pd = er.private_domain
        eco = er.ecosystem
        opc = er.opc

        path_cards = []
        for path in er.strategic_paths:
            path_cards.append(
                ReportCardData(
                    title=f"{path.path_name}（{path.path_type}·{path.recommendation_level}）",
                    subtitle=f"时间范围：{path.timeline}",
                    content=path.expected_outcomes,
                    bullets=[
                        f"投资需求：{path.required_investments}",
                        f"里程碑：{'；'.join(path.key_milestones[:2])}",
                        f"风险提示：{'；'.join(path.major_risks[:2])}",
                    ],
                )
            )

        return ReportSectionData(
            key="endgame",
            title="商业终局设计",
            content=er.overall_narrative,
            bullets=[
                f"私域目标模型：{pd.target_model[:80]}...",
                f"客户留存飞轮：{pd.customer_retention_loop}",
                f"生态定位：{eco.ecosystem_positioning}",
                f"OPC运营平台：{opc.data_flywheel_effect[:80]}...",
                f"推荐路径含有 {len(er.strategic_paths)} 种策略可选",
            ],
            cards=path_cards if path_cards else None,
            note=pd.revenue_impact[:120] + "..." if pd.revenue_impact else None,
        )

    def _build_roadmap(
        self,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> list[ReportRoadmapStage]:
        weakest_blocks = canvas_diagnosis.weakest_blocks or ["待补充"]
        top_names = [item.name for item in scenario_recommendation.top_scenarios]
        first = top_names[0] if top_names else "待补充"
        second = top_names[1] if len(top_names) > 1 else first
        third = top_names[2] if len(top_names) > 2 else second

        return [
            ReportRoadmapStage(
                stage_name="短期：单点提效",
                time_horizon="0-30 天",
                strategic_focus="围绕一个高频、可量化、数据基础相对明确的场景快速试点。",
                priority_actions=[
                    f"围绕 {first} 明确试点目标和验收标准。",
                    f"补齐 {weakest_blocks[0]} 对应的数据口径和流程说明。",
                    "梳理最小可用数据集和人工兜底规则。",
                ],
                expected_outputs=["试点方案", "关键数据清单", "首轮试点复盘纪要"],
            ),
            ReportRoadmapStage(
                stage_name="中期：差异化竞争力",
                time_horizon="31-90 天",
                strategic_focus="把单点试点扩展到相邻流程，形成跨部门协同和可感知业务价值。",
                priority_actions=[
                    f"把 {first} 与 {second} 串联成前后流程闭环。",
                    f"围绕 {weakest_blocks[1] if len(weakest_blocks) > 1 else weakest_blocks[0]} 建立监控与预警。",
                    "沉淀 SOP、异常处理规则和人工接管机制。",
                ],
                expected_outputs=["跨部门协同流程", "阶段经营复盘机制", "可复制场景模板"],
            ),
            ReportRoadmapStage(
                stage_name="长期：生态与增长路径",
                time_horizon="91-180 天",
                strategic_focus="把试点经验沉淀为组织能力，并逐步扩展到更多业务单元和增长场景。",
                priority_actions=[
                    f"推广 {third} 及其相邻方法模板。",
                    "建立统一的知识、数据质量和权限治理机制。",
                    "形成年度 AI 创新项目池和预算讨论机制。",
                ],
                expected_outputs=["组织级 AI 能力框架", "标准化场景资产库", "持续扩展路线图"],
            ),
        ]

    def _build_action_plan(
        self,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
    ) -> list[ReportActionItem]:
        weakest_blocks = canvas_diagnosis.weakest_blocks or ["待补充"]
        top_names = [item.name for item in scenario_recommendation.top_scenarios]
        first = top_names[0] if top_names else "待补充"
        second = top_names[1] if len(top_names) > 1 else first

        return [
            ReportActionItem(
                period="第 1-15 天",
                action="组织一次业务负责人访谈，明确试点目标、边界和成功标准。",
                owner_suggestion="业务负责人 + 数字化负责人",
                deliverable="试点目标说明、指标口径表",
            ),
            ReportActionItem(
                period="第 16-30 天",
                action=f"围绕 {first} 盘点数据源、接口方式和人工校验流程。",
                owner_suggestion="IT / 数据负责人",
                deliverable="最小可用数据清单、数据质量问题列表",
            ),
            ReportActionItem(
                period="第 31-45 天",
                action="完成试点流程梳理，明确人工介入节点和异常兜底规则。",
                owner_suggestion="流程负责人 + 业务骨干",
                deliverable="试点 SOP、异常升级机制",
            ),
            ReportActionItem(
                period="第 46-60 天",
                action=f"开始验证 {first} 业务效果，并同步设计 {second} 的联动方案。",
                owner_suggestion="项目经理 + 业务负责人",
                deliverable="阶段复盘纪要、第二场景方案草稿",
            ),
            ReportActionItem(
                period="第 61-75 天",
                action=f"围绕 {weakest_blocks[0]} 对应问题补齐经营监控指标与看板。",
                owner_suggestion="经营分析负责人",
                deliverable="经营监控看板、预警规则草案",
            ),
            ReportActionItem(
                period="第 76-90 天",
                action="复盘试点经验，决定是否进入跨部门复制与预算化推进。",
                owner_suggestion="管理层 + 项目牵头人",
                deliverable="90 天复盘报告、下一阶段立项建议",
            ),
        ]

    def _build_breakthrough_section(
        self,
        breakthrough_labels: list[str],
        canvas_blocks,
    ) -> ReportSectionData:
        if not breakthrough_labels:
            return ReportSectionData(
                key="breakthrough",
                title="突破要素",
                content="该评估尚未完成突破要素选择。建议先完成商业画布诊断后，围绕最薄弱的 2-3 个要素进行选择和聚焦。",
                note="突破要素选择是 V2 方法论的关键节点，建议在生成最终报告前完成。",
            )

        block_map = {block.key: block for block in canvas_blocks}
        cards: list[ReportCardData] = []
        for label in breakthrough_labels:
            for key, title in ELEMENT_KEY_TO_TITLE.items():
                if title == label:
                    block = block_map.get(key)
                    if block:
                        cards.append(
                            ReportCardData(
                                title=title,
                                subtitle="选定突破要素",
                                content=f"当前状态：{block.current_state}",
                                highlight=f"AI 机会：{block.ai_opportunity}",
                                bullets=[
                                    f"诊断发现：{block.diagnosis}",
                                    f"待补充信息：{block.missing_information}",
                                ],
                            )
                        )
                    else:
                        cards.append(
                            ReportCardData(
                                title=title,
                                subtitle="选定突破要素",
                                content="画布诊断中未找到该要素的详细数据。",
                            )
                        )
                    break

        joined_labels = "、".join(breakthrough_labels)
        return ReportSectionData(
            key="breakthrough",
            title="突破要素",
            content=(
                f"基于商业模式画布诊断结果，本评估选定以下 {len(breakthrough_labels)} 个要素作为"
                f"当前阶段最需要突破的方向：{joined_labels}。"
                f"建议将资源和精力优先聚焦于这些薄弱环节，以最快的速度获得结构性改善。"
            ),
            cards=cards,
            bullets=[
                f"突破方向：{joined_labels}",
                "聚焦 2-3 个关键是避免力量分散、确保落地效果的最佳策略。",
                "每个突破要素对应的 AI 机会可作为后续场景推荐的输入参考。",
            ],
        )

    def _build_direction_section(
        self,
        direction_labels: list[str],
    ) -> ReportSectionData:
        if not direction_labels:
            return ReportSectionData(
                key="direction_expansion",
                title="创新方向延展",
                content="该评估尚未完成创新方向延展。建议先完成突破要素选择后，围绕每个要素展开具体创新方向。",
                note="方向延展是 V2 方法论点阶段的重要环节，建议在生成最终报告前完成。",
            )

        joined = "、".join(direction_labels[:10])
        return ReportSectionData(
            key="direction_expansion",
            title="创新方向延展",
            content=(
                f"基于选定的突破要素，本评估延展出 {len(direction_labels)} 个具体创新方向：{joined}。"
                f"这些方向为后续的 AI 场景推荐和差异化竞争力设计提供了明确抓手。"
            ),
            bullets=[
                f"共计延展 {len(direction_labels)} 个方向",
                "每个方向均对应具体的预期影响和数据需求",
                "后续场景推荐将优先匹配与选定方向高度相关的候选场景",
            ],
            cards=[
                ReportCardData(
                    title=label,
                    content=f"选定创新方向：{label}。详细描述和预期影响请参考方向延展工作台。",
                )
                for label in direction_labels
            ],
            note="方向延展为 V2 方法论点阶段的核心产物，其产出将直接影响后续场景矩阵的生成和竞争力策略的设计。",
        )

    def _resolve_breakthrough_labels(self, breakthrough_keys: list[str]) -> list[str]:
        resolved: list[str] = []
        for key in breakthrough_keys:
            title = ELEMENT_KEY_TO_TITLE.get(key, key)
            if title and title != key:
                resolved.append(title)
            else:
                resolved.append(key)
        return resolved

    def _join_or_todo(self, values: list[str], separator: str = "；") -> str:
        cleaned = [value.strip() for value in values if value and value.strip()]
        return separator.join(cleaned) if cleaned else "待补充"
