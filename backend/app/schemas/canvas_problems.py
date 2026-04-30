"""C1: Nine-Element Problem Library — 画布 9 格标准问题 + 诊断方向库

每格包含 problem_categories，每个类别包含:
- category: 问题类别名
- typical_symptoms: 典型症状/信号
- severity: 严重程度阈值 (高/中/低，取决于症状匹配条数)
- ai_opportunity_template: AI 机会方向模板
- data_gap_indicators: 数据缺口指标
- suggested_questions: 建议追问问题列表
"""

from pydantic import BaseModel, Field


class ProblemCategory(BaseModel):
    category: str
    typical_symptoms: list[str] = Field(default_factory=list)
    severity: str = "中"
    ai_opportunity_template: str = ""
    data_gap_indicators: list[str] = Field(default_factory=list)
    suggested_questions: list[str] = Field(default_factory=list)


class BlockProblemProfile(BaseModel):
    block_key: str
    block_title: str
    problem_categories: list[ProblemCategory] = Field(default_factory=list)


CANVAS_PROBLEM_LIBRARY: list[BlockProblemProfile] = [
    BlockProblemProfile(
        block_key="key_partnerships",
        block_title="关键合作伙伴",
        problem_categories=[
            ProblemCategory(
                category="合作伙伴结构模糊",
                severity="高",
                typical_symptoms=[
                    "未明确合作方类型（供应商/渠道/实施/生态）",
                    "合作方清单缺失或仅有个别名称",
                    "合作模式未区分（战略/项目/交易型）",
                    "没有合作伙伴评估或分级标准",
                ],
                ai_opportunity_template="构建合作方信息图谱和协同风险评估，实现供应商绩效监控与异常预警。",
                data_gap_indicators=["供应商/渠道伙伴名录", "合作模式分类", "合同与结算数据"],
                suggested_questions=[
                    "当前最重要的3-5个合作伙伴是谁？分别属于什么类型？",
                    "合作模式是长期战略、项目制还是交易型？",
                    "是否存在供应商交付质量不稳定或渠道冲突的问题？",
                ],
            ),
            ProblemCategory(
                category="供应链/交付协同不畅",
                severity="高",
                typical_symptoms=[
                    "订单到交付的链路不透明",
                    "多级供应商或渠道伙伴之间信息断裂",
                    "交付异常缺少预警机制",
                    "协同依赖人工沟通，效率低且易出错",
                ],
                ai_opportunity_template="建设供应链数字孪生，实现订单到交付全链路可视化与智能预警。",
                data_gap_indicators=["订单流转数据", "交付时效历史", "异常事件记录"],
                suggested_questions=[
                    "当前从客户下单到交付完成平均需要多少环节、多少天？",
                    "是否出现过因供应商或渠道环节导致的交付延迟？",
                    "合作伙伴之间是否有统一的信息共享平台？",
                ],
            ),
            ProblemCategory(
                category="生态借力意识薄弱",
                severity="中",
                typical_symptoms=[
                    "仅关注自身能力建设，未考虑生态协同",
                    "行业内有可借力的平台或技术伙伴未被识别",
                    "对竞争对手的合作策略缺乏了解",
                    "没有进入生态共建或平台化运营的规划",
                ],
                ai_opportunity_template="梳理行业生态地图，识别可借力的技术和渠道伙伴，降低自身建设成本。",
                data_gap_indicators=["行业生态图谱", "竞品合作分析", "潜在合作方评估"],
                suggested_questions=[
                    "行业内有没有已经成熟的平台或技术方可以合作？",
                    "竞争对手最近和谁在合作？你能否也接触同样的合作方？",
                ],
            ),
        ],
    ),
    BlockProblemProfile(
        block_key="key_activities",
        block_title="关键业务活动",
        problem_categories=[
            ProblemCategory(
                category="核心流程缺乏标准作业",
                severity="高",
                typical_symptoms=[
                    "关键业务活动依赖口头传承而非文档化",
                    "同样的任务不同人做结果差异大",
                    "没有建立标准作业流程(SOP)",
                    "质量或效率的波动主要靠个人能力弥补",
                ],
                ai_opportunity_template="梳理Top 5高频流程，用AI辅助流程挖掘、自动化排程和智能质检。",
                data_gap_indicators=["SOP文档", "流程执行记录", "质检数据"],
                suggested_questions=[
                    "企业最核心的3个业务流程是什么？是否有SOP？",
                    "同一个流程不同人执行的结果差异大吗？",
                    "哪个环节的人工处理时间最长、最容易出错？",
                ],
            ),
            ProblemCategory(
                category="知识沉淀与复用不足",
                severity="高",
                typical_symptoms=[
                    "核心知识存在个人脑中，人走了知识就丢了",
                    "重复性问题被反复回答",
                    "文档散落在多个工具中，检索困难",
                    "新员工学习成本高，上手慢",
                ],
                ai_opportunity_template="构建企业知识库和智能问答系统，实现知识的结构化沉淀与按需检索。",
                data_gap_indicators=["文档系统现状", "知识管理工具", "培训周期数据"],
                suggested_questions=[
                    "如果核心员工离职，他掌握的业务知识能保留多少？",
                    "内部有没有一个统一的、可以搜索的知识库？",
                ],
            ),
            ProblemCategory(
                category="跨部门协同效率低",
                severity="中",
                typical_symptoms=[
                    "跨部门项目信息同步靠邮件和会议",
                    "任务流转存在多次人工转达和重复录入",
                    "部门间数据口径不一致导致重复对账",
                ],
                ai_opportunity_template="引入协同工作流自动化，打通跨部门数据壁垒，建设统一任务看板。",
                data_gap_indicators=["协作工具现状", "跨部门流程节点", "数据口径差异"],
                suggested_questions=[
                    "跨部门项目目前用什么工具协作？信息同步效率如何？",
                    "有没有出现过部门间数据对不上的情况？",
                ],
            ),
        ],
    ),
    BlockProblemProfile(
        block_key="key_resources",
        block_title="关键资源",
        problem_categories=[
            ProblemCategory(
                category="数据资产基础薄弱",
                severity="高",
                typical_symptoms=[
                    "核心业务数据存在多个系统且口径不一致",
                    "数据质量未经审计，存在缺失和错误",
                    "没有统一的数据管理和治理机制",
                    "数据可访问性差，业务部门无法自助使用",
                ],
                ai_opportunity_template="先做数据资产盘点和质量评估，再建立最小可行数据底座支撑 AI 试点。",
                data_gap_indicators=["数据系统清单", "数据质量报告", "数据治理制度"],
                suggested_questions=[
                    "核心业务数据目前分布在几个系统中？数据口径统一吗？",
                    "有没有做过数据质量评估？数据完整性大约在什么水平？",
                ],
            ),
            ProblemCategory(
                category="人才技能缺口",
                severity="中",
                typical_symptoms=[
                    "缺乏数据分析或 AI 相关岗位",
                    "现有团队对新技术的接受度不高",
                    "数字化转型主要由 IT 部门推动，业务参与不足",
                ],
                ai_opportunity_template="优先从低代码或无代码 AI 工具入手，降低技术门槛，同时开展内部数据素养培训。",
                data_gap_indicators=["团队技能矩阵", "培训记录", "数字化项目参与率"],
                suggested_questions=[
                    "现有团队中有没有做过数据分析或AI项目的人？",
                    "员工对使用新工具的态度是积极还是抵触？",
                ],
            ),
            ProblemCategory(
                category="技术基础设施不够",
                severity="中",
                typical_symptoms=[
                    "现有系统老旧，不支持 API 或开放集成",
                    "缺乏云基础设施，系统弹性不足",
                    "信息安全意识和防护措施不足",
                ],
                ai_opportunity_template="评估当前系统架构的 AI 可用性，制定分阶段的技术升级路线。",
                data_gap_indicators=["系统架构文档", "技术债务清单", "安全合规状况"],
                suggested_questions=[
                    "现有核心业务系统是否支持API对接？",
                    "公司数据是否上云？安全合规方面有没有隐患？",
                ],
            ),
        ],
    ),
    BlockProblemProfile(
        block_key="value_propositions",
        block_title="价值主张",
        problem_categories=[
            ProblemCategory(
                category="差异化定位不清晰",
                severity="高",
                typical_symptoms=[
                    "说不清自己与竞品的核心区别",
                    "客户选择你主要是因为关系或价格",
                    '价值主张停留在\u201c质量好、服务好\u201d等泛化表述',
                    "没有量化或可验证的价值差异点",
                ],
                ai_opportunity_template="通过客户反馈和竞品分析数据，提炼可量化的差异化价值点，形成数据支撑的价值主张。",
                data_gap_indicators=["竞品分析", "客户选择理由", "流失原因分析"],
                suggested_questions=[
                    "客户为什么选你们而不是竞争对手？有数据支撑吗？",
                    "如果竞品降价10%，客户还会选你们吗？为什么？",
                ],
            ),
            ProblemCategory(
                category="客户价值传递链路断裂",
                severity="中",
                typical_symptoms=[
                    "销售描述的价值和交付实现的价值有差距",
                    "客户无法感知到服务中的增值部分",
                    "价值传递依赖个别明星员工，无法规模化",
                ],
                ai_opportunity_template="用AI辅助方案自动生成和交付过程透明化，让客户可感知每一步的价值增量。",
                data_gap_indicators=["客户满意度数据", "NPS变化趋势", "交付过程记录"],
                suggested_questions=[
                    "客户在交付过程中能感受到你们方案的独特价值吗？",
                    "有没有做过客户旅程映射？",
                ],
            ),
            ProblemCategory(
                category="定价逻辑缺失",
                severity="低",
                typical_symptoms=[
                    "定价主要参考竞品或成本加成",
                    "没有基于客户价值的定价模型",
                    "不同客户之间的价格差异缺乏逻辑支撑",
                ],
                ai_opportunity_template="分析客户LTV和获客成本，建立基于价值的分层定价模型。",
                data_gap_indicators=["定价历史数据", "竞品价格对比", "客户LTV估算"],
                suggested_questions=[
                    "当前定价策略的依据是什么？",
                    "有没有尝试过不同的定价模式（如订阅制、分层定价）？",
                ],
            ),
        ],
    ),
    BlockProblemProfile(
        block_key="customer_relationships",
        block_title="客户关系",
        problem_categories=[
            ProblemCategory(
                category="客户关系依赖个人",
                severity="高",
                typical_symptoms=[
                    "客户关系主要依赖个别销售或项目经理",
                    "客户信息存在个人微信/邮箱而非系统",
                    "核心客户没有建立多触点关系网络",
                    "人员变动直接导致客户流失风险",
                ],
                ai_opportunity_template="构建客户360视图和关系健康度评分卡，用AI预测流失风险并推荐干预策略。",
                data_gap_indicators=["客户联系记录", "客户互动频次", "客户流失历史"],
                suggested_questions=[
                    "如果负责大客户的销售离职，客户会跟着走吗？",
                    "客户信息目前集中管理还是分散在个人手中？",
                ],
            ),
            ProblemCategory(
                category="客户分层与运营缺位",
                severity="中",
                typical_symptoms=[
                    "对大客户和小客户采用同一服务模式",
                    "没有基于客户价值的差异化运营策略",
                    "客户复购和增购主要靠自然需求驱动",
                ],
                ai_opportunity_template="构建客户分层模型，基于客户价值和行为实施差异化服务与主动运营。",
                data_gap_indicators=["客户交易数据", "客户行为数据", "服务成本数据"],
                suggested_questions=[
                    "你们有没有对客户做过分层（比如按贡献度或活跃度）？",
                    "不同层级的客户享受的服务有区别吗？",
                ],
            ),
            ProblemCategory(
                category="售后与客户成功体系不完善",
                severity="低",
                typical_symptoms=[
                    "售后仅被动响应投诉，没有主动健康监控",
                    "没有客户成功(CS)岗位或机制",
                    "客户续约/复购没有提前预警和干预",
                ],
                ai_opportunity_template="建设客户健康度监控与主动服务触发机制，降低流失并提升NPS。",
                data_gap_indicators=["售后工单数据", "客户投诉记录", "续约率数据"],
                suggested_questions=[
                    "有没有专职的客户成功或售后团队？",
                    "客户续约/复购的决策通常是怎么发生的？",
                ],
            ),
        ],
    ),
    BlockProblemProfile(
        block_key="channels",
        block_title="渠道通路",
        problem_categories=[
            ProblemCategory(
                category="渠道策略不清晰",
                severity="高",
                typical_symptoms=[
                    "没有明确的渠道策略和渠道组合",
                    "获客主要靠口碑或老板人脉",
                    "线上线下渠道没有打通",
                    "渠道数据无法归因分析",
                ],
                ai_opportunity_template="梳理全渠道触点，建立渠道归因模型，用AI辅助渠道组合优化和内容分发。",
                data_gap_indicators=["渠道来源数据", "渠道转化漏斗", "获客成本分渠道"],
                suggested_questions=[
                    "当前客户是通过什么渠道找到你们的？占比各是多少？",
                    "有没有尝试过线上获客？效果如何？",
                ],
            ),
            ProblemCategory(
                category="渠道效率缺乏度量",
                severity="中",
                typical_symptoms=[
                    "不知道每个渠道的获客成本和转化率",
                    "营销投入没有 ROI 分析",
                    "渠道合作伙伴的贡献无法量化评估",
                ],
                ai_opportunity_template="建立渠道效能看板，实现渠道投放的自动化归因和 ROI 实时监控。",
                data_gap_indicators=["渠道投放数据", "转化率数据", "渠道ROI"],
                suggested_questions=[
                    "你们清楚每个渠道带来一个客户要花多少钱吗？",
                    "不同渠道的客户质量有差异吗？",
                ],
            ),
            ProblemCategory(
                category="渠道伙伴管理松散",
                severity="低",
                typical_symptoms=[
                    "渠道伙伴没有分级和考核机制",
                    "伙伴培训和支持不系统",
                    "伙伴合作满意度低，容易流失",
                ],
                ai_opportunity_template="建设渠道伙伴赋能平台，用AI分析伙伴表现并提供个性化支持。",
                data_gap_indicators=["伙伴绩效数据", "伙伴满意度", "伙伴流失率"],
                suggested_questions=[
                    "渠道合作伙伴的活跃度和满意度怎么样？",
                    "有没有对渠道伙伴做过系统的培训和赋能？",
                ],
            ),
        ],
    ),
    BlockProblemProfile(
        block_key="customer_segments",
        block_title="客户细分",
        problem_categories=[
            ProblemCategory(
                category="客户画像粗粒度",
                severity="高",
                typical_symptoms=[
                    "客户仅按行业或规模做了简单分类",
                    "没有多维度客户画像",
                    "不了解不同客户的决策链路和痛点差异",
                    "服务策略一刀切，没有做到按需定制",
                ],
                ai_opportunity_template="利用AI聚类分析构建多维度客户画像，实现按群组定制化服务和内容推荐。",
                data_gap_indicators=["客户属性数据", "客户行为数据", "客户需求标签"],
                suggested_questions=[
                    "你现在能清晰描述3类典型客户画像吗？",
                    "不同客户群体的需求和痛点差异有多大？",
                ],
            ),
            ProblemCategory(
                category="高价值客户识别缺失",
                severity="中",
                typical_symptoms=[
                    "不清楚哪些客户贡献了主要利润",
                    "没有客户LTV（生命周期价值）计算",
                    "营销资源没有向高价值客户倾斜",
                ],
                ai_opportunity_template="构建客户LTV预测模型，识别高价值客户并优化资源配置。",
                data_gap_indicators=["客户交易历史", "客户利润贡献", "服务成本"],
                suggested_questions=[
                    "你知道Top 20%客户贡献了多少收入/利润吗？",
                    "有没有做过客户生命周期的分析？",
                ],
            ),
        ],
    ),
    BlockProblemProfile(
        block_key="cost_structure",
        block_title="成本结构",
        problem_categories=[
            ProblemCategory(
                category="成本结构不透明",
                severity="高",
                typical_symptoms=[
                    "不清楚各项成本占比和变化趋势",
                    "成本核算粒度粗，无法按客户/项目/产品拆分",
                    "没有建立预算和成本控制机制",
                    "隐性成本（如沟通、返工、等待）未被识别",
                ],
                ai_opportunity_template="建立多维度成本分析模型，用AI识别成本异常和隐性浪费，辅助精细化预算。",
                data_gap_indicators=["成本明细数据", "预算执行数据", "项目/客户成本"],
                suggested_questions=[
                    "你知道每个客户或每个项目的利润是多少吗？",
                    "公司最大的成本项是什么？占比多少？有没有优化空间？",
                ],
            ),
            ProblemCategory(
                category="重复劳动推高人力成本",
                severity="中",
                typical_symptoms=[
                    "大量时间花在数据整理、报告制作、信息检索",
                    "同一信息在不同系统中重复录入",
                    "人工排期、审核、核对等环节耗时",
                ],
                ai_opportunity_template="识别Top 3人工重复环节，优先用AI替代或辅助，释放人力到高价值工作。",
                data_gap_indicators=["工时分配数据", "流程耗时分析", "重复任务清单"],
                suggested_questions=[
                    "团队每天大概有多少时间花在重复性工作上？",
                    "如果能节省20%人工处理时间，最想优化哪个环节？",
                ],
            ),
            ProblemCategory(
                category="规模效应未体现",
                severity="低",
                typical_symptoms=[
                    "收入增长但利润率未同步提升",
                    "交付能力的增长需要同步增加人员",
                    "缺乏可复用的标准化组件和服务模板",
                ],
                ai_opportunity_template="梳理可标准化和可复用的服务模块，用AI驱动的知识复用和自动交付降低边际成本。",
                data_gap_indicators=["人效数据", "利润率变化", "项目可复用度"],
                suggested_questions=[
                    "收入每增长10%，成本大约增长多少？",
                    "有没有可以复用的标准方案或服务模板？",
                ],
            ),
        ],
    ),
    BlockProblemProfile(
        block_key="revenue_streams",
        block_title="收入来源",
        problem_categories=[
            ProblemCategory(
                category="收入结构单一",
                severity="高",
                typical_symptoms=[
                    "收入过度依赖单一产品或单一客户群",
                    "缺乏订阅制或持续性服务收入",
                    "增值服务收入占比低",
                    "新业务增长缓慢且贡献有限",
                ],
                ai_opportunity_template="分析客户全生命周期价值，设计多元化收入模型，用AI识别交叉销售和增购机会。",
                data_gap_indicators=["收入构成明细", "客户贡献分析", "产品线利润"],
                suggested_questions=[
                    "最大的单一客户贡献了多少收入？如果流失影响有多大？",
                    "有没有经常性收入（如SaaS订阅、服务年费）？占比多少？",
                ],
            ),
            ProblemCategory(
                category="定价与价值匹配度低",
                severity="中",
                typical_symptoms=[
                    "客户愿意支付的价格低于方案实际价值",
                    "没有分层定价或差异化收费模式",
                    "价格谈判缺乏数据支撑",
                ],
                ai_opportunity_template="构建价值定价模型，基于交付成果和客户收益量化服务价值，支撑定价优化。",
                data_gap_indicators=["报价与成交数据", "客户支付意愿", "竞品价格参照"],
                suggested_questions=[
                    "你们的产品/服务定价有没有随时间调整过？依据是什么？",
                    "客户有没有反馈过价格偏高或偏低？",
                ],
            ),
            ProblemCategory(
                category="商机到收入的转化效率低",
                severity="中",
                typical_symptoms=[
                    "商机转化周期长且不可预测",
                    "赢单率低但原因不清晰",
                    "丢单分析缺失，历史丢单经验未复用",
                ],
                ai_opportunity_template="构建商机评分模型和丢单分析引擎，用AI辅助销售策略优化和预测。",
                data_gap_indicators=["商机漏斗数据", "赢单/丢单原因", "销售周期数据"],
                suggested_questions=[
                    "从商机到签约的平均周期是多长？赢单率大概多少？",
                    "丢单后有没有做过系统性复盘？",
                ],
            ),
        ],
    ),
]

BLOCK_KEY_TO_PROBLEM_PROFILE = {p.block_key: p for p in CANVAS_PROBLEM_LIBRARY}
