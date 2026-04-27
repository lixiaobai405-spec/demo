# 项目总结文档

## 1. 项目概述

本项目是一个面向企业高管/业务负责人的 AI 商业创新方案 Demo 系统，项目名称为 **Meitai AI Business Innovation Agent**。

系统目标是通过一条结构化流程，帮助用户从企业基础信息采集出发，逐步完成：

1. 企业问卷录入
2. 企业画像生成
3. 商业模式画布诊断
4. AI 场景推荐
5. 行业案例匹配
6. 创新报告生成
7. Markdown / DOCX / 打印版导出

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

### 3.4 AI 场景推荐

- 后端提供 `POST /api/assessments/{assessment_id}/scenarios`
- 同时兼容旧接口别名 `scenario-recommendations`
- 推荐逻辑为本地规则评分
- 从知识库场景 YAML 中筛选并输出 Top 场景
- 结果持久化到 `ScenarioRecommendation`

### 3.5 案例匹配

- 后端提供 `POST /api/assessments/{assessment_id}/cases`
- 基于企业画像、画布诊断、场景推荐进行案例匹配
- 结果持久化到 `CaseRecommendation`

### 3.6 报告生成

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

## 4. 核心业务链路

项目当前的推荐使用流程如下：

1. 创建企业问卷
2. 生成企业画像
3. 生成商业画布诊断
4. 生成 AI 场景推荐
5. 生成案例匹配结果
6. 生成创新报告
7. 进入报告详情页查看并导出

从接口依赖关系看，后续步骤依赖前置结果：

- 生成画布前需要企业画像
- 生成案例前需要画像、画布、场景
- 生成报告前需要画像、画布、场景；若案例未生成，系统会在报告生成前自动补齐案例匹配

## 5. 主要接口总览

### 5.1 健康检查

- `GET /health`

### 5.2 Assessment 主流程

- `POST /api/assessments`
- `GET /api/assessments/{assessment_id}`
- `GET /api/assessments/{assessment_id}/report-context`
- `POST /api/assessments/{assessment_id}/profile`
- `POST /api/assessments/{assessment_id}/canvas`
- `POST /api/assessments/{assessment_id}/scenarios`
- `POST /api/assessments/{assessment_id}/cases`
- `POST /api/assessments/{assessment_id}/report?mode=template|llm|template_fallback`

### 5.3 报告

- `GET /api/reports/{report_id}`
- `GET /api/reports/{report_id}/export/markdown`
- `GET /api/reports/{report_id}/export/docx`
- `GET /api/reports/{report_id}/print`

### 5.4 RAG

- `GET /rag/status`
- `POST /rag/search`
- `POST /rag/ingest`

## 6. 数据持久化情况

当前系统具备数据库持久化能力，主要实体包括：

- `Assessment`
- `CanvasDiagnosis`
- `ScenarioRecommendation`
- `CaseRecommendation`
- `GeneratedReport`

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

## 8. 当前项目状态判断

结合代码与文档，当前项目大致处于：

- 主流程已打通
- 前后端可协同运行
- 数据可持久化
- 报告导出已落地
- LLM 增强报告已实现，但依赖环境配置与实际 API 可用性
- RAG 已接入，但默认关闭，且更偏向后续增强能力

因此可以判断：**当前仓库已具备 Demo 演示基础能力，重点不再是“能不能跑通”，而是“输出质量、配置一致性、测试覆盖和文档完善度”。**

## 9. 发现的注意点与已知问题

在查看当前仓库时，发现以下值得注意的地方：

### 9.1 文档与代码存在部分历史差异

旧文档中有些信息已经过期，例如：

- 有些文档仍写“暂不支持导出”，但当前代码已支持 Markdown / DOCX / 打印版导出
- 有些文档把 RAG 接口写成 `/api/rag/*`，但当前实际路由是 `/rag/*`
- 部分旧说明中的技术版本和当前代码不完全一致

因此后续应以当前代码为准，逐步更新旧文档。

### 9.2 端口说明已基本统一

当前项目已统一以前端 `3001` 作为默认开发端口，但仍保留了少量兼容性配置：

- `frontend/package.json` 中开发端口固定为 `3001`
- `AGENTS.md` 也明确要求使用 `3001`
- `.env.example` 已统一为 `http://localhost:3001`
- `scripts/front_start.bat` 已统一提示为 `http://localhost:3001`
- 后端 CORS 仍保留对 `3000` 的兼容，仅用于本地历史环境

虽然不一定导致程序无法运行，但会增加联调时的理解成本。

### 9.3 启动脚本耦合问题已缓解

此前 `scripts/back_start.bat` 中 Python 路径写死，会导致跨机器复用性较差。当前已调整为：

- 优先使用当前环境中的 `python`
- 若不可用则回退到 `py -3`

这样可以降低对固定本机环境的依赖；如果本地 Python 命令不可用，仍建议优先使用命令行方式手动启动。

### 9.4 自动化测试仍偏少

当前仓库能看到较多功能实现代码，但自动化测试覆盖相对有限。项目更像“已完成主链路开发的 Demo 工程”，而不是“高测试覆盖的生产项目”。

## 10. 后续建议

如果继续推进该项目，建议优先处理以下事项：

1. 补充主链路自动化测试，重点覆盖问卷 -> 画像 -> 画布 -> 场景 -> 案例 -> 报告
2. 对 LLM 报告增加更明确的状态提示、超时提示和回退可视化
3. 如果后续要强化知识能力，再继续完善 RAG 数据注入、召回质量和前端展示
4. 补充 PDF 导出与更细的交付版式能力
5. 最后再补更细的权限、日志、审计能力

## 11. 总结

本项目当前已经完成了一个较完整的 AI 商业创新咨询 Demo：

- 有清晰的业务主链路
- 有可运行的前后端
- 有数据库持久化
- 有可选 LLM 增强
- 有报告导出能力
- 有后续可扩展的 RAG 模块

整体来看，项目已经具备演示和继续迭代的基础，下一阶段的重点更适合放在：

- 配置一致性
- 文档统一
- 测试补齐
- 报告质量优化
- RAG 增强
