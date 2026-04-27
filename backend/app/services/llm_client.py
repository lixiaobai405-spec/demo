import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel

from app.core.config import settings
from app.models.assessment import Assessment
from app.schemas.assessment import (
    BusinessModelCanvasResult,
    CanvasBlockResult,
    CompanyProfileResult,
)

PROFILE_SYSTEM_PROMPT = """
你是一名企业战略与 AI 转型顾问。

任务：根据企业问卷生成“企业画像”，输出要具体、简洁、适合业务管理者阅读。

严格要求：
1. 只依据用户提供的信息推断，不要编造 ROI 数字。
2. 不要编造案例名称、客户名称、合作伙伴名称。
3. 缺失信息明确写“待补充”。
4. 当前只生成企业画像，不要输出商业模式画布诊断、场景推荐或报告全文。
5. 输出必须是 JSON，对应以下字段：
   company_name
   company_summary
   value_proposition
   customer_and_market
   operations_and_resources
   digital_and_ai_readiness
   key_challenges
   priority_ai_directions
   missing_information
""".strip()

CANVAS_SYSTEM_PROMPT = """
你是一名企业战略顾问，正在为企业生成 Business Model Canvas（商业模式画布）诊断。

严格要求：
1. 只依据用户提供的信息推断，不要编造 ROI 数字、客户名称、合作伙伴名称。
2. 输出必须覆盖 9 个标准画布模块。
3. 缺失信息明确写“待补充”。
4. 每个模块都要输出：current_state、diagnosis、ai_opportunity、missing_information。
5. 输出必须是 JSON，格式如下：
   overall_summary
   blocks: [
     {
       key,
       title,
       current_state,
       diagnosis,
       ai_opportunity,
       missing_information
     }
   ]

blocks 必须按以下顺序输出 9 项：
key_partnerships
key_activities
key_resources
value_propositions
customer_relationships
channels
customer_segments
cost_structure
revenue_streams
""".strip()

ModelT = TypeVar("ModelT", bound=BaseModel)


class LLMClient:
    def generate_company_profile(
        self,
        assessment: Assessment,
    ) -> tuple[CompanyProfileResult, str]:
        if self._use_mock_mode():
            return self._build_mock_profile(assessment), "mock"

        profile = self._call_live_json_generation(
            model_class=CompanyProfileResult,
            system_prompt=PROFILE_SYSTEM_PROMPT,
            user_prompt=self._build_profile_prompt(assessment),
        )
        return profile, "live"

    def generate_business_model_canvas(
        self,
        assessment: Assessment,
        profile: CompanyProfileResult,
    ) -> tuple[BusinessModelCanvasResult, str]:
        if self._use_mock_mode():
            return self._build_mock_canvas(assessment, profile), "mock"

        canvas = self._call_live_json_generation(
            model_class=BusinessModelCanvasResult,
            system_prompt=CANVAS_SYSTEM_PROMPT,
            user_prompt=self._build_canvas_prompt(assessment, profile),
        )
        return canvas, "live"

    def _use_mock_mode(self) -> bool:
        if settings.llm_mode != "live":
            return True

        return not settings.openai_api_key or not settings.openai_model

    def _call_live_json_generation(
        self,
        model_class: type[ModelT],
        system_prompt: str,
        user_prompt: str,
    ) -> ModelT:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                temperature=0.3,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception:
            response = client.chat.completions.create(
                model=settings.openai_model,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

        raw_content = response.choices[0].message.content or ""
        parsed_content = self._extract_json_object(raw_content)
        payload = json.loads(parsed_content)
        return model_class.model_validate(payload)

    def _build_profile_prompt(self, assessment: Assessment) -> str:
        return f"""
请基于以下企业问卷生成企业画像：

- 企业名称：{self._value_or_placeholder(assessment.company_name)}
- 所属行业：{self._value_or_placeholder(assessment.industry)}
- 企业规模：{self._value_or_placeholder(assessment.company_size)}
- 所在区域：{self._value_or_placeholder(assessment.region)}
- 年营收范围：{self._value_or_placeholder(assessment.annual_revenue_range)}
- 核心产品/服务：{self._value_or_placeholder(assessment.core_products)}
- 目标客户：{self._value_or_placeholder(assessment.target_customers)}
- 当前经营/管理挑战：{self._value_or_placeholder(assessment.current_challenges)}
- 希望通过 AI 达成的目标：{self._value_or_placeholder(assessment.ai_goals)}
- 当前可用数据/系统基础：{self._value_or_placeholder(assessment.available_data)}
- 其他补充信息：{self._value_or_placeholder(assessment.notes)}

请输出结构化 JSON，所有字段都必须存在；列表字段请输出字符串数组。
""".strip()

    def _build_canvas_prompt(
        self,
        assessment: Assessment,
        profile: CompanyProfileResult,
    ) -> str:
        profile_context = f"""
企业画像摘要：
- 企业概览：{profile.company_summary}
- 价值主张：{profile.value_proposition}
- 客户与市场：{profile.customer_and_market}
- 运营与资源基础：{profile.operations_and_resources}
- 数字化与 AI 准备度：{profile.digital_and_ai_readiness}
- 关键挑战：{'；'.join(profile.key_challenges) or '待补充'}
- 优先 AI 切入方向：{'；'.join(profile.priority_ai_directions) or '待补充'}
- 待补充信息：{'；'.join(profile.missing_information) or '待补充'}
""".strip()

        return f"""
请基于以下企业问卷和企业画像，生成 Business Model Canvas 9 格诊断：

企业问卷：
- 企业名称：{self._value_or_placeholder(assessment.company_name)}
- 所属行业：{self._value_or_placeholder(assessment.industry)}
- 企业规模：{self._value_or_placeholder(assessment.company_size)}
- 所在区域：{self._value_or_placeholder(assessment.region)}
- 年营收范围：{self._value_or_placeholder(assessment.annual_revenue_range)}
- 核心产品/服务：{self._value_or_placeholder(assessment.core_products)}
- 目标客户：{self._value_or_placeholder(assessment.target_customers)}
- 当前经营/管理挑战：{self._value_or_placeholder(assessment.current_challenges)}
- 希望通过 AI 达成的目标：{self._value_or_placeholder(assessment.ai_goals)}
- 当前可用数据/系统基础：{self._value_or_placeholder(assessment.available_data)}
- 其他补充信息：{self._value_or_placeholder(assessment.notes)}

{profile_context}

请输出 JSON，包含：
- overall_summary
- blocks（长度必须为 9，且顺序固定）
""".strip()

    def _build_mock_profile(self, assessment: Assessment) -> CompanyProfileResult:
        company_name = self._value_or_placeholder(assessment.company_name)
        industry = self._value_or_placeholder(assessment.industry)
        region = self._value_or_placeholder(assessment.region)
        company_size = self._value_or_placeholder(assessment.company_size)
        revenue_range = self._value_or_placeholder(assessment.annual_revenue_range)
        core_products = self._value_or_placeholder(assessment.core_products)
        target_customers = self._value_or_placeholder(assessment.target_customers)
        current_challenges = self._value_or_placeholder(assessment.current_challenges)
        ai_goals = self._value_or_placeholder(assessment.ai_goals)
        available_data = self._value_or_placeholder(assessment.available_data)
        notes = self._value_or_placeholder(assessment.notes)

        key_challenges = self._split_text_items(assessment.current_challenges)
        priority_ai_directions = self._build_priority_directions(
            assessment.ai_goals,
            assessment.available_data,
        )
        missing_information = self._collect_missing_information(assessment)

        return CompanyProfileResult(
            company_name=company_name,
            company_summary=(
                f"{company_name}是一家位于{region}的{industry}企业，目前处于"
                f"{company_size}规模，年营收范围为{revenue_range}。"
                f"企业当前核心产品或服务是{core_products}，主要服务对象为{target_customers}。"
            ),
            value_proposition=(
                f"从已提供信息看，{company_name}的核心价值主要围绕{core_products}展开，"
                f"重点为{target_customers}提供稳定、可落地的业务支持。"
                f"更细的差异化卖点与定价逻辑目前为{notes if notes != '待补充' else '待补充'}。"
            ),
            customer_and_market=(
                f"企业当前面向的主要客户群体是{target_customers}。"
                f"结合所属行业{industry}判断，后续画像细化时建议补充典型客户类型、采购决策链条和区域市场重点。"
            ),
            operations_and_resources=(
                f"当前问卷显示企业已沉淀的数据或系统基础包括{available_data}。"
                f"这意味着后续 AI 应用推进时，应优先围绕已有流程、已有数据和可快速验证的业务节点切入。"
            ),
            digital_and_ai_readiness=(
                f"企业当前希望通过 AI 达成{ai_goals}，但同时面临{current_challenges}。"
                f"从现有信息判断，企业已具备初步的 AI 探索意愿，下一步关键在于把目标拆解成明确场景，并核实数据质量、负责人和试点范围。"
            ),
            key_challenges=key_challenges,
            priority_ai_directions=priority_ai_directions,
            missing_information=missing_information,
        )

    def _build_mock_canvas(
        self,
        assessment: Assessment,
        profile: CompanyProfileResult,
    ) -> BusinessModelCanvasResult:
        company_name = self._value_or_placeholder(assessment.company_name)
        industry = self._value_or_placeholder(assessment.industry)
        target_customers = self._value_or_placeholder(assessment.target_customers)
        core_products = self._value_or_placeholder(assessment.core_products)
        current_challenges = self._value_or_placeholder(assessment.current_challenges)
        ai_goals = self._value_or_placeholder(assessment.ai_goals)
        available_data = self._value_or_placeholder(assessment.available_data)
        revenue_range = self._value_or_placeholder(assessment.annual_revenue_range)
        notes = self._value_or_placeholder(assessment.notes)

        blocks = [
            CanvasBlockResult(
                key="key_partnerships",
                title="关键合作伙伴",
                current_state=(
                    f"{company_name}的外部协同关系大概率围绕供应商、渠道伙伴、实施服务方或行业生态展开，"
                    "但当前问卷没有给出明确伙伴结构。"
                ),
                diagnosis="合作伙伴信息不完整，供应链协同、交付协同和生态借力路径还不够清晰。",
                ai_opportunity="可优先建设伙伴协同台账、供应与交付风险预警，以及伙伴知识检索能力。",
                missing_information="供应商结构、渠道模式、实施伙伴与合作分工待补充。",
            ),
            CanvasBlockResult(
                key="key_activities",
                title="关键业务活动",
                current_state=(
                    f"企业当前关键活动主要围绕{core_products}的销售、交付、实施或服务展开，"
                    f"并受到“{current_challenges}”的直接影响。"
                ),
                diagnosis="销售推进、协同交付和知识沉淀等关键活动存在效率波动。",
                ai_opportunity=f"建议围绕{ai_goals}优先识别 1 到 2 个高频流程节点，做智能辅助与流程预警。",
                missing_information="关键流程节点、负责人分工、标准作业流程待补充。",
            ),
            CanvasBlockResult(
                key="key_resources",
                title="关键资源",
                current_state=f"企业的核心资源包括行业经验、产品能力、客户关系以及现有数据/系统基础：{available_data}。",
                diagnosis="已有一定数字化基础，但数据口径、知识沉淀和跨部门共享机制仍需进一步确认。",
                ai_opportunity="可先把 CRM、ERP、工单、文档等资源统一梳理，形成可用于 AI 试点的最小数据底座。",
                missing_information="关键系统清单、数据质量现状、知识文档分布待补充。",
            ),
            CanvasBlockResult(
                key="value_propositions",
                title="价值主张",
                current_state=f"{company_name}当前面向{target_customers}提供的核心价值主要围绕{core_products}展开。",
                diagnosis="价值主张已具备业务基础，但差异化优势、响应速度和服务体验的表达还不够结构化。",
                ai_opportunity="可以用 AI 强化方案生成、客户响应、知识复用和服务一致性，提升价值交付效率。",
                missing_information="核心卖点排序、典型客户选择依据、竞争差异点待补充。",
            ),
            CanvasBlockResult(
                key="customer_relationships",
                title="客户关系",
                current_state=f"企业当前客户关系管理应主要依赖销售和交付团队，对象集中在{target_customers}。",
                diagnosis="客户关系维护容易依赖个人经验，难以规模复制。",
                ai_opportunity="可优先部署线索跟进提醒、客户问答助手、商机摘要和流失预警，强化关系管理。",
                missing_information="客户分层机制、服务 SLA、复购与续约流程待补充。",
            ),
            CanvasBlockResult(
                key="channels",
                title="渠道通路",
                current_state="当前问卷尚未明确直销、渠道、线上获客、线下拜访或服务网络等具体通路。",
                diagnosis="渠道通路信息缺失，会影响获客效率判断、客户触达成本评估和场景优先级排序。",
                ai_opportunity="建议补齐渠道旅程后，再引入渠道转化分析、内容辅助生成和渠道贡献评估。",
                missing_information="主要获客渠道、客户触达路径、渠道伙伴贡献待补充。",
            ),
            CanvasBlockResult(
                key="customer_segments",
                title="客户细分",
                current_state=f"问卷显示当前主要客户群为{target_customers}，但细分维度和优先级尚未充分展开。",
                diagnosis="客户细分已有方向，但还需从行业、规模、场景、区域和决策链条继续细化。",
                ai_opportunity="可用 AI 做客户画像聚类、需求标签提取和高潜客识别，提升客户分层质量。",
                missing_information="客户分层标准、典型画像、决策角色与采购周期待补充。",
            ),
            CanvasBlockResult(
                key="cost_structure",
                title="成本结构",
                current_state=f"结合{industry}行业和当前业务阶段，主要成本大概率集中在人力、交付、运营协同、系统维护和获客投入。",
                diagnosis="如果流程协同不稳、知识复用不足，单位项目或单位客户服务成本可能被重复劳动拉高。",
                ai_opportunity="建议用 AI 优先压缩重复沟通、人工整理、信息检索和异常追踪成本。",
                missing_information="成本结构拆分、交付成本口径、营销成本与人工占比待补充。",
            ),
            CanvasBlockResult(
                key="revenue_streams",
                title="收入来源",
                current_state=f"企业当前收入主要来自{core_products}相关业务，年营收范围为{revenue_range}。",
                diagnosis="现有收入来源具备基础，但问卷尚未体现一次性收入、持续服务收入和增值收入的构成比例。",
                ai_opportunity="可通过 AI 提升商机转化率、交付复用率和客户续约/复购机会识别能力。",
                missing_information=f"收入结构拆分、毛利结构、订阅或服务化收入情况待补充。补充说明：{notes}",
            ),
        ]

        return BusinessModelCanvasResult(
            overall_summary=(
                f"{company_name}当前的商业模式基础已经围绕“{core_products} -> {target_customers} -> {revenue_range}”形成闭环，"
                "但渠道结构、合作伙伴、成本结构和客户分层的细化信息仍不足。"
                f"结合当前挑战“{current_challenges}”，后续更适合先从销售协同、交付协同、知识沉淀等高频流程切入 AI。"
            ),
            blocks=blocks,
        )

    def _collect_missing_information(self, assessment: Assessment) -> list[str]:
        missing_fields: dict[str, Any] = {
            "企业名称": assessment.company_name,
            "所属行业": assessment.industry,
            "企业规模": assessment.company_size,
            "所在区域": assessment.region,
            "年营收范围": assessment.annual_revenue_range,
            "核心产品/服务": assessment.core_products,
            "目标客户": assessment.target_customers,
            "当前经营/管理挑战": assessment.current_challenges,
            "AI 目标": assessment.ai_goals,
            "可用数据/系统基础": assessment.available_data,
        }

        missing = [
            label
            for label, value in missing_fields.items()
            if self._value_or_placeholder(value) == "待补充"
        ]

        if not missing:
            return ["目前问卷核心字段已填写，建议后续补充客户决策链、关键流程节点和数据口径说明。"]

        return missing

    def _build_priority_directions(
        self,
        ai_goals: str | None,
        available_data: str | None,
    ) -> list[str]:
        goal_text = self._value_or_placeholder(ai_goals)
        data_text = self._value_or_placeholder(available_data)

        return [
            f"围绕“{goal_text}”拆分 1 到 2 个可验证的试点场景",
            f"盘点并清洗现有数据基础：{data_text}",
            "明确业务负责人、试点流程和验收口径，避免目标过大导致落地失焦",
        ]

    def _split_text_items(self, text: str | None) -> list[str]:
        normalized = self._value_or_placeholder(text)

        if normalized == "待补充":
            return ["当前经营/管理挑战待补充"]

        parts = [
            item.strip("；;，,。 ")
            for item in re.split(r"[；;。\n]+", normalized)
            if item.strip("；;，,。 ")
        ]

        if parts:
            return parts[:5]

        return [normalized]

    def _value_or_placeholder(self, value: str | None) -> str:
        if value is None:
            return "待补充"

        cleaned = value.strip()
        return cleaned or "待补充"

    def _extract_json_object(self, content: str) -> str:
        stripped = content.strip()

        if stripped.startswith("{") and stripped.endswith("}"):
            return stripped

        fenced_match = re.search(r"```json\s*(\{.*\})\s*```", stripped, re.DOTALL)
        if fenced_match:
            return fenced_match.group(1)

        generic_match = re.search(r"(\{.*\})", stripped, re.DOTALL)
        if generic_match:
            return generic_match.group(1)

        raise ValueError("LLM response did not contain a valid JSON object.")
