# B1 课前输入与初始化导入设计

## 1. 文档目的

本文档用于定义阶段 B1 的最小可落地方案，目标是在不破坏现有 Assessment 主流程的前提下，为系统补齐：

- 课前输入模板
- 初始化导入链路
- 自动预填策略
- 来源标记与人工校正机制

本文档面向产品、后端、前端三方，作为后续接口设计和实现拆分的依据。

## 2. 当前现状

当前系统的主入口是 `POST /api/assessments`，要求用户一次性填写以下字段：

- `company_name`
- `industry`
- `company_size`
- `region`
- `annual_revenue_range`
- `core_products`
- `target_customers`
- `current_challenges`
- `ai_goals`
- `available_data`
- `notes`

这些字段已经足以驱动后续画像、画布、场景、案例和报告主链路，但仍存在三个明显问题：

1. 用户必须直接进入问卷填写，无法先提交课前材料
2. 半结构化材料无法被系统吸收为初始上下文
3. 问卷字段与用户原始材料之间没有“来源关系”和“待确认边界”

因此，B1 的目标不是替换现有问卷，而是在它之前增加一个“导入并预填”的前置步骤。

## 3. 设计目标

B1 阶段只解决最小闭环，不追求一步做到完整知识抽取。

### 3.1 本阶段要做到

- 支持提交课前输入文本或 Markdown 内容
- 将原始输入解析为结构化字段建议
- 将可确认内容映射到 Assessment 表单预填
- 将不适合直接入库的内容作为补充上下文保留
- 让用户看到每个字段来自“原文 / 系统推断 / 待补充”

### 3.2 本阶段不做

- 不直接替代现有 `POST /api/assessments`
- 不在首版引入复杂文件解析链路，如 PDF / DOCX 二进制上传
- 不把系统推断结果直接视为用户确认事实
- 不要求真实 LLM 才能完成导入

## 4. 输入范围设计

### 4.1 首版支持的输入形态

建议首版只支持以下两类：

1. 结构化表单补充输入
2. 一段或多段纯文本 / Markdown 粘贴内容

原因：

- 实现成本低
- 与当前前端表单形态兼容
- 便于后续扩展到文件上传
- 避免首版被文档解析细节拖慢

### 4.2 后续再扩展的输入形态

以下能力不进入 B1 首版，但在接口设计上预留：

- `.md` 文件上传
- `.docx` 文件上传
- PDF 文本抽取
- 多附件合并导入

## 5. 课前输入模板

建议把课前输入拆成两层：必填业务信息 + 可选上下文补充。

### 5.1 必填字段

这些字段优先映射到现有 Assessment：

| 模板字段 | 对应 Assessment 字段 | 说明 |
| --- | --- | --- |
| 企业名称 | `company_name` | 必填 |
| 所属行业 | `industry` | 必填 |
| 企业规模 | `company_size` | 必填 |
| 所在区域 | `region` | 必填 |
| 年营收范围 | `annual_revenue_range` | 必填 |
| 核心产品/服务 | `core_products` | 必填 |
| 目标客户 | `target_customers` | 必填 |
| 当前经营/管理挑战 | `current_challenges` | 必填 |
| 希望通过 AI 达成的目标 | `ai_goals` | 必填 |
| 当前可用数据/系统基础 | `available_data` | 必填 |
| 其他补充说明 | `notes` | 可选 |

### 5.2 扩展补充字段

这些字段不直接进入现有 Assessment 主表，建议先保留在导入结果中：

- 业务场景背景
- 当前商业模式画布现状描述
- 已知瓶颈流程
- 关键岗位或负责人
- 当前项目约束
- 已尝试过的 AI 或数字化动作
- 对报告的重点关注项

这些字段可以在后续版本用于：

- 画像增强
- 画布预填
- 风险说明
- 讲师点评上下文

## 6. 数据分层设计

为避免“原始材料”和“最终问卷值”混在一起，建议把导入数据拆成三层。

### 6.1 原始输入层

记录用户提交的原始材料，不做强结构约束。

建议结构：

```json
{
  "source_type": "text|markdown|form",
  "raw_content": "用户粘贴的原始内容",
  "attachments": [],
  "submitted_at": "2026-04-28T10:00:00Z"
}
```

### 6.2 解析结果层

记录系统从原始内容中抽取出的字段候选值、证据片段和置信状态。

建议结构：

```json
{
  "field_candidates": {
    "company_name": {
      "value": "测试连锁零售企业",
      "source": "原文",
      "confidence": "high",
      "evidence": "企业名称：测试连锁零售企业"
    },
    "ai_goals": {
      "value": "提升门店运营效率，增强会员复购",
      "source": "推断",
      "confidence": "medium",
      "evidence": "希望用 AI 稳定门店管理并提升复购"
    }
  },
  "unmapped_notes": [
    "提到区域试点，但未写明负责人"
  ],
  "warnings": [
    "年营收范围未明确，需要用户确认"
  ]
}
```

### 6.3 标准化结果层

记录真正准备用于预填问卷的数据，字段必须与 Assessment 创建结构兼容。

建议结构：

```json
{
  "assessment_prefill": {
    "company_name": "测试连锁零售企业",
    "industry": "零售",
    "company_size": "100-499人",
    "region": "华东",
    "annual_revenue_range": "待确认",
    "core_products": "社区零售门店、会员运营与到家服务",
    "target_customers": "社区家庭用户、周边白领与会员客户",
    "current_challenges": "门店运营效率波动，会员复购不稳定",
    "ai_goals": "提升门店运营效率，增强会员复购",
    "available_data": "POS、会员系统、商品主数据",
    "notes": "计划先从单区域试点推进"
  },
  "field_meta": {
    "company_name": {
      "source_type": "raw",
      "status": "confirmed"
    },
    "annual_revenue_range": {
      "source_type": "missing",
      "status": "needs_user_confirmation"
    },
    "ai_goals": {
      "source_type": "inferred",
      "status": "needs_user_confirmation"
    }
  }
}
```

## 7. 字段映射策略

### 7.1 可直接预填字段

满足以下条件的字段可直接进入预填结果：

- 原文明确出现
- 含义和 Assessment 字段一一对应
- 不依赖复杂推断

例如：

- 企业名称
- 所属行业
- 企业规模
- 所在区域
- 核心产品/服务

### 7.2 需用户确认字段

以下情况只生成建议值，不直接视为已确认：

- 需要归纳总结才能得到的字段
- 原文表述模糊
- 存在多个候选值
- 属于系统推断而非用户直述

例如：

- `ai_goals`
- `current_challenges`
- `annual_revenue_range`
- `available_data`

### 7.3 暂不入库字段

以下内容先保留在导入结果中，不写入 Assessment：

- 当前商业模式画布的长文本描述
- 对竞争对手的补充说明
- 对讲师关注重点的要求
- 对项目边界的额外约束

## 8. 自动预填边界

### 8.1 预填到哪里

B1 首版建议只做两类预填：

1. Assessment 问卷字段预填
2. 企业画像生成前的补充上下文挂载

不建议 B1 首版直接写入：

- `CanvasDiagnosis`
- `ScenarioRecommendation`
- `CaseRecommendation`
- `GeneratedReport`

### 8.2 对画布的处理方式

画布相关内容如果在原始材料中出现，首版只做“候选上下文保存”，不直接落成 9 宫格结果。

建议后续在 B2 或 B1.5 再增加：

- 画布草稿预填
- “待确认”的格子级建议
- 来源回显

### 8.3 来源标记规范

每个预填字段都应带上来源标签，至少包含：

- `raw`：用户原文直接提供
- `inferred`：系统归纳或推断
- `missing`：当前无法得出，需要用户补充

同时配合状态字段：

- `confirmed`
- `needs_user_confirmation`
- `needs_user_input`

## 9. 接口设计建议

首版建议把“导入”和“正式创建 Assessment”拆成两个接口，避免破坏现有主流程。

### 9.1 导入解析接口

`POST /api/intake/import`

用途：

- 接收课前输入
- 返回解析结果和预填建议
- 不直接创建 Assessment

建议请求结构：

```json
{
  "source_type": "markdown",
  "raw_content": "# 企业课前输入\n\n企业名称：测试连锁零售企业",
  "structured_fields": {
    "company_name": "测试连锁零售企业"
  }
}
```

建议响应结构：

```json
{
  "import_session_id": "uuid",
  "assessment_prefill": {},
  "field_meta": {},
  "unmapped_notes": [],
  "warnings": []
}
```

### 9.2 基于导入结果创建 Assessment

`POST /api/intake/import/{import_session_id}/assessment`

用途：

- 用户确认预填后，正式创建 Assessment
- 将确认后的字段写入现有 Assessment 表

建议请求结构：

```json
{
  "confirmed_assessment_input": {
    "company_name": "测试连锁零售企业",
    "industry": "零售",
    "company_size": "100-499人",
    "region": "华东",
    "annual_revenue_range": "5000万-1亿元",
    "core_products": "社区零售门店、会员运营与到家服务",
    "target_customers": "社区家庭用户、周边白领与会员客户",
    "current_challenges": "门店运营效率波动，会员复购不稳定",
    "ai_goals": "提升门店运营效率，增强会员复购",
    "available_data": "POS、会员系统、商品主数据",
    "notes": "计划先从单区域试点推进"
  }
}
```

### 9.3 保持现有主流程兼容

保留现有：

- `POST /api/assessments`

这样用户有两条入口：

1. 直接填问卷
2. 先导入，再确认并创建问卷

## 10. 服务设计建议

建议新增三个服务职责，而不是把逻辑堆进现有画像或报告服务。

### 10.1 `IntakeParser`

职责：

- 解析原始文本
- 提取字段候选值
- 生成证据片段和 warning

首版可先用规则 + 轻量模板实现，后续再接 LLM 增强。

### 10.2 `IntakeNormalizer`

职责：

- 把候选字段映射成 Assessment 可用结构
- 统一枚举值和文案格式
- 标记 `raw / inferred / missing`

### 10.3 `IntakeSessionService`

职责：

- 持久化导入会话
- 返回预填结果
- 在用户确认后创建 Assessment

## 11. 持久化建议

建议新增导入会话实体，例如 `AssessmentIntakeSession`，而不是把未确认内容直接放进 `Assessment`。

建议字段：

- `id`
- `source_type`
- `raw_content`
- `parsed_payload`
- `normalized_payload`
- `status`
- `created_assessment_id`
- `created_at`
- `updated_at`

状态建议：

- `draft`
- `parsed`
- `confirmed`
- `discarded`

## 12. 前端交互建议

首版前端建议使用三步式流程：

1. 输入课前材料
2. 查看系统预填建议
3. 用户确认后创建 Assessment

### 12.1 页面核心区块

- 原始输入区
- 结构化字段建议区
- 来源标签区
- warning 区
- “确认创建问卷”按钮

### 12.2 用户体验原则

- 系统推断必须显式标注
- 缺失字段要醒目标记
- 用户必须能手动覆盖所有预填值
- 不应让用户误以为导入后就等于完成问卷确认

## 13. 风险与应对

### 风险 1：错误推断污染主流程

应对：

- 导入与正式创建拆接口
- 所有推断字段默认要求用户确认

### 风险 2：首版范围过大

应对：

- 首版只做文本 / Markdown 粘贴
- 文件上传和复杂解析延后

### 风险 3：与现有问卷产生双入口混乱

应对：

- 保留直接创建入口
- 在前端明确“快速填写”和“导入预填”是两种模式

### 风险 4：过早依赖真实 LLM

应对：

- 首版先用规则与模板抽取
- LLM 只作为后续增强选项

## 14. MVP 验收标准

B1 MVP 完成时，应至少满足：

1. 用户可提交一段课前输入文本或 Markdown
2. 系统可返回 Assessment 字段级预填建议
3. 每个字段都能看到来源与确认状态
4. 用户确认后能创建现有 Assessment
5. 不经过导入时，原有 `POST /api/assessments` 仍可正常使用
6. 导入失败或字段缺失时，系统能给出显式 warning，而不是静默吞掉

## 15. 建议实施顺序

### 第一步：文档与数据结构

- 明确字段模板
- 定义 intake session schema
- 定义导入接口 contract

### 第二步：后端最小实现

- 新增 intake session 存储
- 新增导入解析接口
- 新增确认创建 Assessment 接口

### 第三步：前端最小实现

- 新增导入页
- 新增字段确认页
- 接入现有 Assessment 创建后续跳转

### 第四步：补充验证

- 为导入 -> 确认 -> 创建 Assessment 增加自动化测试
- 覆盖缺失字段、推断字段、正常创建三类场景

## 16. 与后续阶段的关系

B1 只是入口层能力，完成后可作为以下能力的前置基础：

- B2 的突破要素选择
- 画像增强与画布草稿预填
- 课后跟进上下文沉淀
- 更细的知识库召回与个性化推荐

因此，B1 的关键不是“导入得多复杂”，而是先把“原始输入 -> 结构化建议 -> 用户确认 -> 主流程创建”这条链路定义稳定。
