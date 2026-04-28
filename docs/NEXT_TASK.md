# Next Task: B1 课前输入与初始化导入设计

## Objective

在 A3 主流程测试基线已经补齐后，进入阶段 B1，设计“课前输入文档 + 初始化导入 + 自动预填”的最小可落地方案。

## Context

A2 与 A3 当前状态：

- A2 验收已完成，真 LLM 报告的 Markdown / DOCX / 打印版导出链路已验证通过
- A3 主流程测试已形成可重复执行的后端回归基线
- `backend/tests/test_api_main_flow.py` 当前结果为 `7 passed, 1 skipped`
- 已覆盖主链路、模板模式、LLM 回退、导出接口、关键错误路径
- 已新增 cases 自动补齐、`/scenario-recommendations` 旧别名兼容、缺失 `report_id` 的 `404`
- 真 LLM 成功路径为可选集成测试，默认不跑，仅在本地显式开启

下一步不再是继续补 A3，而是把阶段 B 的第一个高优先级能力定义清楚。

## Sub-tasks

### 1. 明确课前输入范围
**Files**: `docs/*`, `backend/app/schemas/*`

- [ ] 确定首版支持的输入形态：文本 / Markdown / 表单 / 粘贴内容
- [ ] 梳理课前输入必须字段与可选字段
- [ ] 明确哪些字段直接映射到 Assessment
- [ ] 明确哪些字段作为补充上下文暂存

### 2. 设计初始化导入链路
**Files**: `backend/app/api/routes/*`, `backend/app/services/*`

- [ ] 设计导入接口或导入步骤入口
- [ ] 定义原始输入、解析结果、标准化结果三层结构
- [ ] 设计失败回退与人工补充机制
- [ ] 保证导入能力不破坏现有问卷主流程

### 3. 设计自动预填策略
**Files**: `backend/app/services/*`, `frontend/*`

- [ ] 明确可自动预填的画像字段
- [ ] 明确可自动预填的画布格子范围
- [ ] 标记“用户原始输入 / 系统推断 / 待补充”三类来源
- [ ] 避免把推断结果误当成已确认事实

### 4. 明确验收与验证方式
**Files**: `docs/*`, `backend/tests/*`

- [ ] 定义 B1 的最小验收用例
- [ ] 规划导入后到问卷/画像预填的验证路径
- [ ] 明确何时需要新增自动化测试
- [ ] 保留模板兜底与显式 warning 机制

## Acceptance Criteria

1. 课前输入模板与字段映射关系清晰
2. 初始化导入链路有明确的接口/服务设计
3. 自动预填边界清楚，不会混淆事实与推断
4. 新能力不破坏现有 Assessment 主流程
5. B1 的最小实现范围与后续扩展边界已文档化

## Current Regression Baseline

```bash
cd backend
pytest tests/test_api_main_flow.py

# Optional: run the live LLM success-path test locally only
set RUN_LIVE_LLM_TESTS=true
pytest tests/test_api_main_flow.py -k live_llm
```

## Current Design Output

- `docs/B1_PRE_INPUT_IMPORT_DESIGN.md` - B1 课前输入与初始化导入设计稿，包含输入范围、数据分层、接口建议、预填边界、前端交互与 MVP 验收标准

## Files to Modify

1. `docs/B1_PRE_INPUT_IMPORT_DESIGN.md` - B1 方案主文档
2. `docs/PROJECT_ADVANCEMENT_PLAN.md` - 阶段 B1 方案同步
3. `docs/PROJECT_SUMMARY_CN.md` - 如有需要，补充导入能力定位
4. `backend/app/schemas/*` - 导入数据结构设计
5. `backend/app/services/*` - 解析与标准化服务设计

## Constraints

- 不破坏现有问卷录入主链路
- 不默认引入对真实 LLM 的强依赖
- 不把推断字段直接写成已确认事实
- 保留模板兜底、显式 warning 与人工修正入口
