from app.schemas.assessment import CanvasDiagnosisResult
from app.schemas.competitiveness import CompetitivenessResult
from app.schemas.endgame import (
    ENDGAME_KNOWLEDGE,
    EndgameResult,
    EcosystemDesign,
    OPCDesign,
    PrivateDomainDesign,
    StrategicPath,
    ThreeStageStrategy,
    ThreeStageStrategyStage,
)
from app.schemas.direction import DirectionSuggestion
from app.schemas.breakthrough import ELEMENT_KEY_TO_TITLE


class EndgameAnalyzer:
    INDUSTRY_MAP = {
        "制造": "制造",
        "制造业": "制造",
        "生产制造": "制造",
        "供应链科技": "制造",
        "供应链": "制造",
        "物流": "制造",
        "零售": "零售",
        "零售业": "零售",
        "电商": "零售",
        "消费": "零售",
        "科技": "科技",
        "互联网": "科技",
        "软件": "科技",
        "SaaS": "科技",
    }

    def analyze(
        self,
        industry: str,
        canvas_diagnosis: CanvasDiagnosisResult,
        breakthrough_keys: list[str],
        selected_directions: list[DirectionSuggestion],
        competitiveness_result: CompetitivenessResult | None,
    ) -> EndgameResult:
        industry_type = self._detect_industry(industry)
        private_domain = self._build_private_domain(industry_type, canvas_diagnosis)
        ecosystem = self._build_ecosystem(industry_type, canvas_diagnosis)
        opc = self._build_opc(industry_type, canvas_diagnosis, breakthrough_keys)
        three_stage_strategy = self._build_three_stage_strategy(
            canvas_diagnosis, breakthrough_keys, competitiveness_result
        )
        paths = self._build_strategic_paths(
            industry_type, canvas_diagnosis, breakthrough_keys, competitiveness_result
        )
        narrative = self._build_narrative(
            private_domain, ecosystem, opc, three_stage_strategy, paths, competitiveness_result
        )

        return EndgameResult(
            generation_mode="rule_based",
            private_domain=private_domain,
            ecosystem=ecosystem,
            opc=opc,
            three_stage_strategy=three_stage_strategy,
            strategic_paths=paths,
            overall_narrative=narrative,
        )

    def _detect_industry(self, industry: str) -> str:
        for keyword, mapped in self.INDUSTRY_MAP.items():
            if keyword in str(industry or ""):
                return mapped
        return "通用"

    def _build_private_domain(
        self,
        industry_type: str,
        canvas: CanvasDiagnosisResult,
    ) -> PrivateDomainDesign:
        templates = ENDGAME_KNOWLEDGE["private_domain_templates"]
        template = templates.get(industry_type, templates["通用"])

        current_vp = None
        for block in canvas.canvas.blocks:
            if block.key == "customer_relationships":
                current_vp = block
                break
        current_state = (
            current_vp.current_state
            if current_vp
            else "当前客户关系管理数据不完整"
        )

        return PrivateDomainDesign(
            current_state=current_state,
            target_model=template["target_model"],
            key_strategies=list(template["strategies"]),
            customer_retention_loop=template["retention_loop"],
            revenue_impact=(
                f"预计通过私域体系建设，可提升客户复购率15-25%，"
                f"降低获客成本30-40%，客户生命周期价值有望增长2-3倍。"
            ),
        )

    def _build_ecosystem(
        self,
        industry_type: str,
        canvas: CanvasDiagnosisResult,
    ) -> EcosystemDesign:
        templates = ENDGAME_KNOWLEDGE["ecosystem_templates"]
        template = templates.get(industry_type, templates["通用"])

        return EcosystemDesign(
            ecosystem_positioning=template["positioning"],
            key_partners_to_engage=list(template["partners"]),
            orchestration_strategy=template["orchestration"],
            platform_effect=template["platform_effect"],
        )

    def _build_opc(
        self,
        industry_type: str,
        canvas: CanvasDiagnosisResult,
        breakthrough_keys: list[str],
    ) -> OPCDesign:
        templates = ENDGAME_KNOWLEDGE["opc_templates"]
        template = templates.get(industry_type, templates["通用"])

        from app.schemas.breakthrough import ELEMENT_KEY_TO_TITLE

        bt_labels = [ELEMENT_KEY_TO_TITLE.get(k, k) for k in breakthrough_keys[:2]]

        return OPCDesign(
            operations_excellence=(
                f"围绕{'、'.join(bt_labels)}等突破要素，"
                f"{template['operations']}"
            ),
            platform_capability=template["platform"],
            content_and_community=template["content_community"],
            data_flywheel_effect=template["data_flywheel"],
        )

    def _build_three_stage_strategy(
        self,
        canvas: CanvasDiagnosisResult,
        breakthrough_keys: list[str],
        competitiveness_result: CompetitivenessResult | None,
    ) -> ThreeStageStrategy:
        """将三阶段推进策略统一收口到商业终局结果。"""
        if competitiveness_result is not None:
            strategy = competitiveness_result.delivery_strategy
            return ThreeStageStrategy(
                stage_1=ThreeStageStrategyStage(
                    title="阶段 1",
                    focus="快速验证",
                    strategy="选择最高价值、最低风险的单一场景进行端到端试点，集中资源跑通最小闭环。",
                    objective=strategy.phase_1_quick_win,
                    key_actions=[
                        "明确试点场景边界与成功标准（量化 KPI）",
                        "组建 3-5 人专职小组，指定业务负责人",
                        "跑通数据采集 → 模型训练 → 结果验证全流程",
                        "产出试点复盘报告，沉淀可复用的方法模板",
                    ],
                    key_risks=[
                        "试点范围过大导致资源分散、周期拉长",
                        "缺少专职负责人，推进节奏容易失焦",
                    ],
                ),
                stage_2=ThreeStageStrategyStage(
                    title="阶段 2",
                    focus="规模扩展",
                    strategy="将试点验证有效的模式复制到相邻业务单元，同步补齐数据与组织短板。",
                    objective=strategy.phase_2_scale,
                    key_actions=[
                        "将试点方法论模板化，推广至 2-3 个相邻场景",
                        "建立统一数据底座，打通跨部门数据孤岛",
                        "组建跨部门协同机制，明确各方职责与考核",
                        "持续监控扩展效果，动态调整优先级与资源分配",
                    ],
                    key_risks=[
                        "跨部门协同若缺少统一目标会削弱扩展效果",
                        "快速扩展可能导致数据质量和模型效果下降",
                    ],
                ),
                stage_3=ThreeStageStrategyStage(
                    title="阶段 3",
                    focus="壁垒构建",
                    strategy="将已验证能力沉淀为组织标准、平台能力与数据资产，形成可持续竞争壁垒。",
                    objective=strategy.phase_3_moat,
                    key_actions=[
                        "将核心能力 API 化/平台化，支撑多业务线复用",
                        "建立 AI 能力持续迭代的组织机制与人才梯队",
                        "构建数据飞轮，形成业务数据 → 模型优化 → 业务提升的正循环",
                        "沉淀行业知识资产与最佳实践，建立品牌护城河",
                    ],
                    key_risks=[
                        "组织惯性可能导致创新动力衰减",
                        "竞争对手可能同步采取类似策略，需持续创新保持领先",
                    ],
                ),
                key_risks=list(strategy.key_risks),
            )

        breakthrough_labels = [ELEMENT_KEY_TO_TITLE.get(key, key) for key in breakthrough_keys[:2]]
        joined = "、".join(breakthrough_labels) if breakthrough_labels else "关键能力"
        weakest = "、".join(canvas.weakest_blocks[:2]) if canvas.weakest_blocks else "关键薄弱环节"
        return ThreeStageStrategy(
            stage_1=ThreeStageStrategyStage(
                title="阶段 1",
                focus="快速验证",
                strategy="选择最高价值、最低风险的单一场景进行端到端试点，集中资源跑通最小闭环。",
                objective=f"围绕{joined}先完成最小试点闭环，验证业务价值与组织协同方式。",
                key_actions=[
                    "明确试点场景边界与成功标准（量化 KPI）",
                    "组建 3-5 人专职小组，指定业务负责人",
                    "跑通数据采集 → 模型训练 → 结果验证全流程",
                    "产出试点复盘报告，沉淀可复用的方法模板",
                ],
                key_risks=[
                    "试点范围过大导致资源分散、周期拉长",
                    "缺少专职负责人，推进节奏容易失焦",
                ],
            ),
            stage_2=ThreeStageStrategyStage(
                title="阶段 2",
                focus="规模扩展",
                strategy="将试点验证有效的模式复制到相邻业务单元，同步补齐数据与组织短板。",
                objective=f"把试点经验扩展到相邻流程与团队，并同步修补{weakest}等关键短板。",
                key_actions=[
                    "将试点方法论模板化，推广至 2-3 个相邻场景",
                    "建立统一数据底座，打通跨部门数据孤岛",
                    "组建跨部门协同机制，明确各方职责与考核",
                    "持续监控扩展效果，动态调整优先级与资源分配",
                ],
                key_risks=[
                    "跨部门协同若缺少统一目标会削弱扩展效果",
                    "快速扩展可能导致数据质量和模型效果下降",
                ],
            ),
            stage_3=ThreeStageStrategyStage(
                title="阶段 3",
                focus="壁垒构建",
                strategy="将已验证能力沉淀为组织标准、平台能力与数据资产，形成可持续竞争壁垒。",
                objective="将已验证能力沉淀为组织标准、平台能力与经营机制，形成长期竞争壁垒。",
                key_actions=[
                    "将核心能力 API 化/平台化，支撑多业务线复用",
                    "建立 AI 能力持续迭代的组织机制与人才梯队",
                    "构建数据飞轮，形成业务数据 → 模型优化 → 业务提升的正循环",
                    "沉淀行业知识资产与最佳实践，建立品牌护城河",
                ],
                key_risks=[
                    "组织惯性可能导致创新动力衰减",
                    "竞争对手可能同步采取类似策略，需持续创新保持领先",
                ],
            ),
            key_risks=[
                "若试点阶段缺少明确负责人，推进节奏容易失焦。",
                "跨部门协同若缺少统一目标，会削弱规模扩展效果。",
            ],
        )

    def _build_strategic_paths(
        self,
        industry_type: str,
        canvas: CanvasDiagnosisResult,
        breakthrough_keys: list[str],
        competitiveness_result: CompetitivenessResult | None,
    ) -> list[StrategicPath]:
        score = canvas.overall_score
        weakest = "、".join(canvas.weakest_blocks[:2]) if canvas.weakest_blocks else "薄弱环节"

        conservative = StrategicPath(
            path_name="稳健试点路径",
            path_type="保守",
            execution_rhythm="先完成单点试点验证，再根据反馈逐步复制到相邻业务单元。",
            key_milestones=[
                "完成数据盘点并明确首批高价值试点场景。",
                "上线试点闭环，验证客户经营与组织协同方式。",
                "将已验证做法复制到相邻业务单元并固化方法模板。",
                "形成可复用的私域运营标准，并评估是否进入生态协同阶段。",
            ],
            capability_requirements="适合优先复用现有业务负责人、轻量工具能力和基础数据治理机制。",
            expected_outcomes=(
                "形成可复制的客户经营样板，为后续生态扩展沉淀稳定的数据和方法资产。"
            ),
            major_risks=[
                f"如果{weakest}等环节数据基础薄弱，私域效果可能在早期不达预期。",
                "组织可能缺乏私域运营专职团队和对应考核机制。",
            ],
            recommendation_level="推荐" if score < 85 else "可选",
        )

        balanced = StrategicPath(
            path_name="均衡推进路径",
            path_type="均衡",
            execution_rhythm="试点验证与生态协同并行推进，边验证边扩展，逐步形成联动闭环。",
            key_milestones=[
                "同步启动私域试点与关键生态伙伴协同方案设计。",
                "打通基础数据流与协作接口，形成最小联动闭环。",
                "在验证有效后逐步扩展合作范围与业务触点。",
                "沉淀平台化能力雏形，形成可持续的数据协同机制。",
            ],
            capability_requirements="需要业务、运营、数据与外部伙伴形成稳定协同，并具备跨流程推进能力。",
            expected_outcomes=(
                "同时推进私域沉淀与生态协同，逐步形成可放大的增长引擎与协作网络。"
            ),
            major_risks=[
                "资源同步投入私域和生态可能导致资源不足，优先级需要动态调整。",
                f"生态伙伴的数据协同和利益分配机制需要在项目早期明确。",
            ],
            recommendation_level="推荐" if score >= 75 else "可选",
        )

        aggressive = StrategicPath(
            path_name="平台化突破路径",
            path_type="激进",
            execution_rhythm="以平台化重构为主线快速推进，集中资源同步拉通能力、伙伴与运营机制。",
            key_milestones=[
                "快速搭建私域基础能力并完成首批种子用户与伙伴接入。",
                "同步推进规模化运营和开放能力的最小版本落地。",
                "扩大生态参与范围，验证多边协同的正向反馈。",
                "完成平台化升级，形成商业终局雏形与数据飞轮。", 
            ],
            capability_requirements="需要强执行团队、跨部门授权机制以及稳定的平台建设和运营承接能力。",
            expected_outcomes=(
                "快速建立平台化差异化壁垒，推动多边协同与网络效应进入正循环。"
            ),
            major_risks=[
                "推进速度过快可能导致组织能力、技术架构和数据质量方面的隐患。",
                "平台模式需要足够的双边用户规模才能形成正向飞轮，早期可能 ROI 较低。",
                "竞争对手可能同步采取类似策略，需要持续创新保持领先。",
            ],
            recommendation_level="可选",
        )

        return [conservative, balanced, aggressive]

    def _build_narrative(
        self,
        private_domain: PrivateDomainDesign,
        ecosystem: EcosystemDesign,
        opc: OPCDesign,
        three_stage_strategy: ThreeStageStrategy,
        paths: list[StrategicPath],
        competitiveness_result: CompetitivenessResult | None,
    ) -> str:
        recommended_path = next((p for p in paths if p.recommendation_level == "推荐"), paths[0])

        parts = [
            "本评估的核心商业终局判断如下：",
            "",
            f"【私域】{private_domain.target_model}",
            f"客户留存飞轮：{private_domain.customer_retention_loop}",
            "",
            f"【生态】{ecosystem.ecosystem_positioning}",
            f"关键合作伙伴：{'、'.join(ecosystem.key_partners_to_engage[:3])}",
            "",
            f"【OPC 运营平台能力】{opc.data_flywheel_effect}",
            "",
            (
                f"【三阶段推进】先{three_stage_strategy.stage_1.focus}，"
                f"再{three_stage_strategy.stage_2.focus}，最终{three_stage_strategy.stage_3.focus}。"
            ),
            "",
            (
                f"【推荐路径】{recommended_path.path_name}（{recommended_path.path_type}策略，"
                f"{recommended_path.execution_rhythm}）"
            ),
        ]

        if competitiveness_result is not None:
            parts.append(
                f"该路径与已建立的{len(competitiveness_result.advantages)}个核心竞争优势形成协同共振。"
            )

        return "\n".join(parts)
