from app.schemas.assessment import CanvasDiagnosisResult
from app.schemas.competitiveness import CompetitivenessResult
from app.schemas.endgame import (
    ENDGAME_KNOWLEDGE,
    EndgameResult,
    EcosystemDesign,
    OPCDesign,
    PrivateDomainDesign,
    StrategicPath,
)
from app.schemas.direction import DirectionSuggestion


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
        paths = self._build_strategic_paths(
            industry_type, canvas_diagnosis, breakthrough_keys, competitiveness_result
        )
        narrative = self._build_narrative(
            private_domain, ecosystem, opc, paths, competitiveness_result
        )

        return EndgameResult(
            generation_mode="rule_based",
            private_domain=private_domain,
            ecosystem=ecosystem,
            opc=opc,
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
            timeline="9-12 个月",
            key_milestones=[
                "Month 1-2: 完成数据盘点，确定 1 个高价值私域试点场景",
                "Month 3-4: 私域试点上线，验证客户留资和复购改善效果",
                "Month 5-8: 基于试点数据迭代，将私域能力扩展至第 2 个业务单元",
                "Month 9-12: 形成可复制的私域运营标准，评估生态合作可行性",
            ],
            required_investments="投入 2-3 名运营人员 + 轻量 CRM/CDP 工具，首年预算控制在 80-150 万。",
            expected_outcomes=(
                f"私域留资率提升 20-30%，复购率提升 10-15%，"
                f"为后续生态扩展积累核心客户数据资产。"
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
            timeline="6-9 个月",
            key_milestones=[
                "Month 1-2: 同步启动私域试点和 1 个关键生态伙伴的合作谈判",
                "Month 3-4: 私域 MVP + 生态连接器上线，打通数据流",
                "Month 5-6: 验证公私域联动效果，扩展至 3-5 个生态合作方",
                "Month 7-9: 构建平台化能力雏形，形成数据飞轮初步闭环",
            ],
            required_investments="组建 3-5 人增长 + 平台团队，技术投资约 200-400 万，生态合作投入视行业而定。",
            expected_outcomes=(
                "同时推进私域留资和生态流量，预期 6 个月内形成公私域联动的初步增长引擎。"
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
            timeline="4-6 个月",
            key_milestones=[
                "Month 1: 完成私域基础架构搭建和首批种子用户导入",
                "Month 2-3: 私域规模化运营 + 开放平台 MVP 上线",
                "Month 4-5: 引入 10+ 生态合作伙伴，启动多边网络效应",
                "Month 6: 完成平台化升级，构建数据飞轮和商业终局雏形",
            ],
            required_investments="组建 8-12 人专项团队，技术+运营总投入约 500-1000 万，需要较强组织执行力支撑。",
            expected_outcomes=(
                "快速建立平台差异化壁垒，在 6 个月内形成网络效应和多边协同的商业终局架构。"
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
            f"【OPC 运营平台能力】{opc.data_flywheel_effect[:120]}...",
            "",
            f"【推荐路径】{recommended_path.path_name}（{recommended_path.path_type}策略，{recommended_path.timeline}）",
        ]

        if competitiveness_result is not None:
            parts.append(
                f"该路径与已建立的{len(competitiveness_result.advantages)}个核心竞争优势形成协同共振。"
            )

        return "\n".join(parts)
