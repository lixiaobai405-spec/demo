# 项目总结文档

## 1. 项目概述

本项目是一个面向企业高管/业务负责人的 AI 商业创新方案 Demo 系统，项目名称为 **Meitai AI Business Innovation Agent**。

系统目标是通过一条结构化流程，帮助用户从企业基础信息采集出发，逐步完成：

1. 企业问卷录入
2. 企业画像生成
3. 商业模式画布诊断（九要素问题库增强）
4. 突破要素推荐与选择
5. 创新方向延展
6. 差异化竞争力分析
7. 商业终局设计（私域 + 生态 + OPC）
8. AI 场景推荐（方向加权）
9. 分层案例匹配（行业→规模→痛点→方向 + 来源标注）
10. 创新报告生成（14 章节 + 质量审计）
11. Markdown / DOCX / 打印版 / PDF 导出
12. 课后 30 天跟进任务管理
13. 双周案例推送与方案再校准
14. 讲师工作台（分组/批量点评/CSV 导出）

从当前代码实现来看，这已经不是纯静态原型，而是一个具备前后端联动、数据库持久化、报告导出和可选 LLM/RAG 能力的可运行 Demo。

## 2. 技术架构

### 2.1 后端

- 框架：FastAPI
- ORM：SQLAlchemy
- 数据库：SQLite
- AI 接入：OpenAI 兼容接口
- 报告导出：Markdown / HTML / DOCX
- 可选检索：ChromaDB

后端目录核心位于 `backend/app`，主要分层如下：

- `api/routes`：接口路由
- `core`：环境配置
- `db`：数据库初始化与会话管理
- `models`：数据模型
- `schemas`：Pydantic 数据结构
- `services`：企业画像、场景推荐、报告生成等业务逻辑
- `exporters`：Markdown、HTML、DOCX 导出实现
- `rag`：RAG 检索相关模块
- `prompts`：LLM 报告写作提示词

### 2.2 前端

- 框架：Next.js 15
- UI：React + Tailwind CSS
- 语言：TypeScript

前端目录核心位于 `frontend/src`：

- `app`：页面路由
- `components`：业务组件
- `lib/api.ts`：前端 API 调用封装
- `lib/types.ts`：前后端交互类型定义

### 2.3 数据与知识库

- `backend/data`：SQLite 数据库、Chroma 数据持久化目录
- `knowledge/raw`：场景库、案例库、报告模板、风险手册等知识文件

## 3. 当前功能实现情况

根据代码和仓库内容，当前项目主要能力如下。

### 3.1 企业问卷与流程管理

- 支持创建 Assessment 记录
- 支持通过 `assessment_id` 查询完整聚合状态
- 支持流程进度恢复
- 支持页面刷新后按 ID 回看历史结果

这是整条业务链路的入口与主线。

### 3.2 企业画像生成

- 后端提供 `POST /api/assessments/{assessment_id}/profile`
- 支持通过 LLM 客户端生成企业画像
- 当配置不足时，可退回到 Mock / 模板化能力
- 结果持久化到 Assessment 记录中

### 3.3 商业模式画布诊断

- 后端提供 `POST /api/assessments/{assessment_id}/canvas`
- 生成 9 宫格商业模式画布诊断内容
- 自动计算整体评分、薄弱模块、建议聚焦点
- 结果持久化到 `CanvasDiagnosis`

### 3.4 突破要素与方向延展

- 后端提供 `POST /api/assessments/{id}/breakthrough/recommend` + `/select`
- 9 要素评分，推荐 2-3 个关键突破方向
- 后端提供 `POST /api/assessments/{id}/directions/expand` + `/select`
- 每突破要素生成 3 个创新方向建议（含预期影响、所需数据、关联场景类别）
- 已选方向可加权到后续场景推荐中

### 3.5 竞争力分析与商业终局

- 后端提供 `POST /api/assessments/{id}/competitiveness/generate`
- VP 重构 + 点到线竞争力串联 + 4 象限差异化策略
- 后端提供 `POST /api/assessments/{id}/endgame/generate`
- 私域目标模型 + 生态定位 + OPC 运营平台 + 3 路径推演（保守/均衡/激进）

### 3.6 AI 场景推荐

- 后端提供 `POST /api/assessments/{assessment_id}/scenarios`
- 同时兼容旧接口别名 `scenario-recommendations`
- 推荐逻辑为本地规则评分
- 从知识库场景 YAML 中筛选并输出 Top 场景
- 结果持久化到 `ScenarioRecommendation`

### 3.7 分层案例匹配

- 后端提供 `POST /api/assessments/{assessment_id}/cases`
- 4 层检索：行业 → 规模 → 痛点 → 方向
- 每案例输出 `source_summary` 标注匹配来源层级
- 23 个行业案例库，14 个行业近亲家族
- 结果持久化到 `CaseRecommendation`

### 3.8 报告生成

- 后端提供 `POST /api/assessments/{assessment_id}/report`
- 支持 `template`、`llm`、`template_fallback` 三种模式
- 模板报告始终是主兜底能力
- 若启用 LLM 报告能力但模型不可用，会自动回退到模板模式
- 报告结果保存到 `GeneratedReport`

当前报告链路不是简单文本拼接，而是结构化报告数据 + Markdown / HTML 渲染 + 导出能力。

### 3.7 报告导出与展示

已实现以下能力：

- 获取报告详情：`GET /api/reports/{report_id}`
- 导出 Markdown：`GET /api/reports/{report_id}/export/markdown`
- 导出 DOCX：`GET /api/reports/{report_id}/export/docx`
- 打印版 HTML：`GET /api/reports/{report_id}/print`

前端也已提供：

- 报告生成页
- 报告文档预览页
- Markdown / Word / 打印版导出入口

### 3.8 RAG 检索

RAG 模块代码已经接入，默认关闭。

已实现接口：

- `GET /rag/status`
- `POST /rag/search`
- `POST /rag/ingest`

说明：

- 当前 RAG 路由未挂在 `/api/rag`，而是直接挂在 `/rag`
- 是否启用由 `RAG_ENABLED` 环境变量控制
- 需要先注入知识库才能得到有效检索结果
- 未配置真实 embedding 时会进入 mock embedding 模式，仅适合演示

### 3.10 质量审计

- 报告生成时自动执行质量审计
- 14 章节逐级评分（6 规则校验）
- 3 级置信度标注（高/中/低）+ 来源归属
- API: `GET /api/reports/{report_id}/quality`

### 3.11 课后跟进

- 后端提供 `GET/PATCH /api/assessments/{id}/follow-up`
- 6 项默认 30 天跟进任务（3 个时间窗口）
- 4 态流转：pending → in_progress → completed / blocked
- 进展备注 + 阻塞标记

### 3.12 双周案例推送

- 后端提供 `POST /api/assessments/{id}/push`
- 每轮推送 2 个新案例（去重 + 分层检索）
- 6 轮次阶段化学习笔记
- 方案再校准：批量完成任务 + 追加新行动项

### 3.13 讲师工作台

- 后端提供 `GET /api/instructor/dashboard`
- 全学员推进状态总览（分组筛选 + 完成率统计）
- 批量点评 + CSV 导出
- 前端学员/讲师双视角 Tab 切换

## 4. 核心业务链路

当前完整链路：

```
导入 → 画像 → 画布 → 突破 → 方向 → 竞争力 → 
商业终局 → 场景 → 案例 → 报告(14章) → 导出/分享 → 
课后跟进(30天) → 双周推送 → 讲师工作台
```

从接口依赖关系看，后续步骤依赖前置结果。级联清空机制保证：重生成上游模块时，下游结果自动失效。

## 5. 主要接口总览

### 5.1 健康检查

- `GET /health`

### 5.2 Assessment 主流程

- `POST /api/assessments`
- `GET /api/assessments/{id}`
- `POST /api/assessments/{id}/profile`
- `POST /api/assessments/{id}/canvas`
- `POST /api/assessments/{id}/breakthrough/recommend`
- `POST /api/assessments/{id}/breakthrough/select`
- `POST /api/assessments/{id}/directions/expand`
- `POST /api/assessments/{id}/directions/select`
- `POST /api/assessments/{id}/competitiveness/generate`
- `POST /api/assessments/{id}/endgame/generate`
- `POST /api/assessments/{id}/scenarios`
- `POST /api/assessments/{id}/cases`
- `POST /api/assessments/{id}/report?mode=template|llm`
- `GET /api/assessments/{id}/report-context`

### 5.3 报告与导出

- `GET /api/reports/{report_id}`
- `GET /api/reports/{report_id}/export/markdown`
- `GET /api/reports/{report_id}/export/docx`
- `GET /api/reports/{report_id}/export/pdf`
- `GET /api/reports/{report_id}/print`
- `GET /api/reports/{report_id}/enrich`
- `GET /api/reports/{report_id}/quality`
- `POST /api/reports/{report_id}/share`
- `GET /api/reports/{report_id}/share/{token}`

### 5.4 课后跟进与推送

- `GET /api/assessments/{id}/follow-up`
- `PATCH /api/assessments/{id}/follow-up/tasks/{task_id}`
- `POST /api/assessments/{id}/follow-up/recalibrate`
- `POST /api/assessments/{id}/push`
- `GET /api/assessments/{id}/push/history`
- `POST /api/assessments/{id}/recalibrate`

### 5.5 讲师视角

- `GET /api/instructor/dashboard`
- `POST /api/instructor/batch-comment`
- `GET /api/instructor/export?format=csv`

### 5.6 RAG

- `GET /rag/status`
- `POST /rag/search`
- `POST /rag/ingest`

## 6. 数据持久化情况

当前系统具备数据库持久化能力，主要实体包括：

- `Assessment` — 企业问卷（含 class_group, instructor_comment）
- `CanvasDiagnosis` — 画布诊断
- `BreakthroughSelection` — 突破要素选择
- `DirectionSelection` — 方向选择
- `CompetitivenessAnalysis` — 竞争力分析
- `EndgameAnalysis` — 商业终局分析
- `ScenarioRecommendation` — 场景推荐
- `CaseRecommendation` — 案例匹配
- `GeneratedReport` — 报告（含 quality_json）
- `FollowUpTask` — 课后跟进任务
- `PushRecord` — 案例推送记录

此外，企业画像当前存放在 `Assessment.profile_payload` 字段中。

从现有实现看，数据库在应用启动时自动初始化，适合 Demo 环境快速启动。

## 7. 运行方式

## 7.1 默认端口

- 前端：`3001`
- 后端：`8000`

注意：前端 `package.json` 中已经把开发端口固定为 `3001`。

## 7.2 环境变量

建议先复制：

```powershell
Copy-Item .env.example .env
```

关键配置项如下：

```env
APP_NAME="Meitai AI Business Innovation Agent API"
APP_ENV="development"
FRONTEND_ORIGIN="http://localhost:3001"
DATABASE_URL="sqlite:///./backend/data/meitai_demo.db"
LLM_MODE="mock"
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
OPENAI_API_KEY=""
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_MODEL="your-model-name"
RAG_ENABLED="false"
CHROMA_PERSIST_DIR="./backend/data/chroma"
RAG_TOP_K="5"
```

补充说明：

- 如果要启用 LLM 深度报告，还需要补充 `LLM_REPORT_ENABLED=true`
- 若未配置 `OPENAI_API_KEY` 或 `OPENAI_MODEL`，LLM 报告会回退到模板模式
- 当前环境模板已统一使用 `http://localhost:3001` 作为前端默认地址

## 7.3 启动命令

### 后端

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 前端

```powershell
cd frontend
npm install
npm run dev
```

## 8. 当前项目状态

当前项目已完成 14 步完整链路，具备：

- 主流程全部打通（V2 方法论 4 个新增模块已实现）
- 前后端协同运行
- 11 个数据模型的完整持久化
- 报告 4 种格式导出（MD/DOCX/Print/PDF）
- LLM 增强报告 + Mock 兜底
- RAG 已接入，默认关闭
- 19 backend + 6 frontend + 26 step E2E 测试

**当前仓库已具备 Demo 演示基础能力，重点从"能跑通"转向"输出质量和配置一致性"。**

## 9. 文档与代码一致性

本文档已与当前代码主分支同步（2025-06-29）。关键统一项：

- 前端端口统一为 3001
- RAG 路由为 `/rag`（非 `/api/rag`）
- 报告 14 章节，非早期版本的 11 或 13 章
- 后端现存 19 passed / 1 skipped 测试，非早期个位数

## 10. 后续建议

1. 配真实 OpenAI Key 跑全链路 LLM 模式验证
2. Docker 一键部署 (`docker-compose up`)
3. 20-50 人课堂并发验证
4. i18n 多语言支持

## 11. 总结

本项目已完成一个完整的 AI 商业创新咨询 Demo：

- 14 步全链路（问卷→画像→画布→突破→方向→竞争力→商业终局→场景→案例→报告→导出→跟进→推送→讲师）
- 前后端协同运行 + 11 模型持久化
- 4 格式报告导出 + LLM 增强 + 质量审计
- 课后 30 天跟进 + 双周案例推送 + 讲师工作台
- 分层案例检索 + 九要素问题库 + 行业近亲映射
- 26 步 E2E 全链路回归测试
