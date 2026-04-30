# 美太 AI 商业创新智能体 — 项目架构与实现总览

> 最后更新：2025-07-01

## 一、项目简介

**Meitai AI Business Innovation Agent** 是一个面向企业高管/业务负责人的 AI 商业创新方案 Demo 系统。

一句话描述：**引导企业完成从问卷录入到课后跟进的 14 步完整 AI 创新链路，最终输出一份 14 章节的结构化报告。**

---

## 二、技术架构

```
┌──────────────────────────────────────────────────────────┐
│                     用户浏览器                             │
│                  http://localhost:3001                    │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│              前端 (Next.js 15 + TypeScript + Tailwind)    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │ 首页     │ │ 问卷页   │ │ 报告页   │ │ 导入页      │ │
│  │ /        │ │ /assess..│ │ /report  │ │ /intake     │ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────────┘ │
│  组件：assessment-workbench / instructor-dashboard /     │
│        follow-up-dashboard / push-panel / endgame-panel  │
└─────────────────────┬────────────────────────────────────┘
                      │ REST API (JSON)
                      ▼
┌──────────────────────────────────────────────────────────┐
│              后端 (FastAPI + SQLAlchemy + SQLite)         │
│                                                          │
│  /api/assessments/*    核心流程（14 模块）                 │
│  /api/reports/*        报告生成/导出/分享                  │
│  /api/instructor/*     讲师工作台                         │
│  /rag/*                RAG 知识库检索（可选）              │
│                                                          │
│  services/                                             │
│  ├── llm_client.py           LLM 客户端                  │
│  ├── case_matcher.py         案例匹配引擎                │
│  ├── layered_retriever.py    分层检索器                  │
│  ├── quality_checker.py      质量审计                    │
│  ├── follow_up_service.py    课后跟进                    │
│  ├── push_service.py         双周推送                    │
│  └── instructor_service.py   讲师服务                    │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│                   数据层                                  │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ SQLite     │  │ knowledge/   │  │ DeepSeek API     │ │
│  │ (11 模型)   │  │ raw/*.yaml   │  │ (可选 LLM)       │ │
│  └────────────┘  └──────────────┘  └──────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### 技术栈明细

| 层 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Next.js | 15.5 |
| UI | React 18 + Tailwind CSS | — |
| 后端框架 | FastAPI | ≥0.103 |
| ORM | SQLAlchemy | ≥2.0 |
| 数据库 | SQLite | — |
| AI | OpenAI 兼容接口 (DeepSeek) | 可选 |
| 向量检索 | ChromaDB | 可选 |
| 报告导出 | python-docx / PyMuPDF | — |
| 容器化 | Docker + docker-compose | — |
| 语言 | Python 3.11 / TypeScript | — |

---

## 三、数据库模型（11 个实体）

```
assessments                    # 企业问卷（含 class_group, instructor_comment）
canvas_diagnosis               # 商业模式画布 9 格诊断
breakthrough_selections        # 突破要素选择
direction_selections           # 创新方向选择
competitiveness_analyses       # 差异化竞争力分析
endgame_analyses               # 商业终局设计
scenario_recommendations       # AI 场景推荐
case_recommendations           # 案例匹配
generated_reports              # 报告（含 quality_json）
follow_up_tasks                # 课后跟进任务
push_records                   # 双周案例推送记录
```

所有表由 SQLAlchemy `create_all()` 启动时自动创建。

---

## 四、完整 14 步业务链路

```
步骤1    创建问卷（支持 DOCX/PDF 导入预填）
           │
步骤2    生成企业画像（Mock / LLM）
           │
步骤3    商业模式画布 9 格诊断（九要素问题库增强）
           │
步骤4    突破要素推荐 + 选择（9 要素评分）
           │
步骤5    创新方向延展（6 方向/要素 + 预期影响 + 数据需求）
           │
步骤6    差异化竞争力分析（VP 重构 + 点到线串联 + 4 象限策略）
           │
步骤7    商业终局设计（私域目标模型 + 生态定位 + OPC + 3 路径推演）
           │
步骤8    AI 场景推荐（方向加权，规则评分）
           │
步骤9    分层案例匹配（行业→规模→痛点→方向 + 来源标注）
           │
步骤10   报告生成（14 章模板 / LLM 增强，失败自动回退）
           │
步骤11   报告导出（Markdown / DOCX / 打印版 / PDF）
           │
步骤12   课后 30 天跟进（6 项任务 + 4 态流转 + 阻塞标记 + 进展备注）
           │
步骤13   双周案例推送（去重 + 6 轮次学习笔记 + 方案再校准）
           │
步骤14   讲师工作台（分组筛选 + 批量点评 + CSV 导出 + 学员/讲师双视角）
```

### 级联清空机制

重生成上游模块（如画布）→ 下游结果（突破/方向/竞争力/场景/案例/报告）自动失效。

---

## 五、报告结构（14 章）

| # | 章节 |
|:---:|------|
| 1 | 企业基本画像 |
| 2 | 当前商业模式画布诊断 |
| 3 | 突破要素 |
| 4 | 创新方向延展 |
| 5 | AI 成熟度评估 |
| 6 | 高优先级 AI 提效场景 |
| 7 | 推荐场景详细规划 |
| 8 | 差异化竞争力设计 |
| 9 | 参考案例与启示 |
| 10 | 三阶段 AI 创新路线图 |
| 11 | 90 天行动计划 |
| 12 | 风险与阻力 |
| 13 | 讲师点评区 |
| 14 | 商业终局设计 |

---

## 六、知识库与智能增强

### 六.1 九要素问题库
- 9 画布格子 × 26 问题类别 × 81 症状
- 每问题含：诊断方向、追问引导
- 接入画布诊断 Canvas System Prompt

### 六.2 分层案例检索
- 4 层匹配：行业（14 家族近亲映射）→ 规模（6 级层级）→ 痛点 → 方向
- 每案例输出 `source_summary` 溯源至层级
- 23 个行业案例库

### 六.3 质量审计系统
- 14 章节逐级评分（6 规则校验）
- 3 级置信度标注（高/中/低）
- "缺失关键数据"/"无法完成诊断" 检测

### 六.4 LLM 报告增强
- DeepSeek v4 Flash 验证通过
- `response_format={"type":"json_object"}` JSON 模式
- 全链路 ~3,000-5,000 tokens，~¥0.003-0.005/次
- 失败自动回退模板模式

---

## 七、API 端点总览（35+）

### 核心流程（17 端点）
| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/assessments` | 创建问卷 |
| `GET` | `/api/assessments/{id}` | 聚合状态 |
| `POST` | `/api/assessments/{id}/profile` | 企业画像 |
| `POST` | `/api/assessments/{id}/canvas` | 画布诊断 |
| `POST` | `/api/assessments/{id}/breakthrough/recommend` | 突破推荐 |
| `POST` | `/api/assessments/{id}/breakthrough/select` | 突破选择 |
| `POST` | `/api/assessments/{id}/directions/expand` | 方向延展 |
| `POST` | `/api/assessments/{id}/directions/select` | 方向选择 |
| `GET` | `/api/assessments/{id}/directions` | 已选方向 |
| `POST` | `/api/assessments/{id}/competitiveness/generate` | 竞争力 |
| `POST` | `/api/assessments/{id}/endgame/generate` | 商业终局 |
| `POST` | `/api/assessments/{id}/scenarios` | 场景推荐 |
| `POST` | `/api/assessments/{id}/cases` | 案例匹配 |
| `POST` | `/api/assessments/{id}/report` | 生成报告 |
| `GET` | `/api/assessments/{id}/report-context` | 报告上下文 |

### 报告与导出（9 端点）
| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/reports/{report_id}` | 报告详情 |
| `GET` | `/api/reports/{report_id}/export/markdown` | MD 导出 |
| `GET` | `/api/reports/{report_id}/export/docx` | DOCX 导出 |
| `GET` | `/api/reports/{report_id}/export/pdf` | PDF 导出 |
| `GET` | `/api/reports/{report_id}/print` | 打印版 |
| `GET` | `/api/reports/{report_id}/enrich` | 报告增强 |
| `GET` | `/api/reports/{report_id}/quality` | 质量审计 |
| `POST` | `/api/reports/{report_id}/share` | 分享链接 |
| `GET` | `/api/reports/{report_id}/share/{token}` | 访问分享 |

### 课后跟进（6 端点）
| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/assessments/{id}/follow-up` | 跟进计划 |
| `PATCH` | `/api/assessments/{id}/follow-up/tasks/{task_id}` | 更新任务 |
| `POST` | `/api/assessments/{id}/follow-up/recalibrate` | 复盘修订 |
| `POST` | `/api/assessments/{id}/push` | 案例推送 |
| `GET` | `/api/assessments/{id}/push/history` | 推送历史 |
| `POST` | `/api/assessments/{id}/recalibrate` | 再校准 |

### 讲师视角（3 端点）
| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/instructor/dashboard` | 学员总览 |
| `POST` | `/api/instructor/batch-comment` | 批量点评 |
| `GET` | `/api/instructor/export?format=csv` | CSV 导出 |

### RAG（3 端点，默认关闭）
| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/rag/status` | RAG 状态 |
| `POST` | `/rag/search` | 搜索知识库 |
| `POST` | `/rag/ingest` | 注入知识 |

---

## 八、测试覆盖

```
后端单元+集成：19 passed, 1 skipped（Live LLM opt-in）
前端组件测试：6 passed
E2E 全链路：25 步骤（问卷→画像→画布→突破→方向→竞争力→商业终局→
                       场景→案例→报告→导出→分享→跟进→推送→讲师→级联清空）
TypeScript 检查：0 errors
```

---

## 九、部署方式

### Docker 一键部署（推荐）

```bash
docker compose up
```

浏览器打开 `http://localhost:3001` 即用。

- 不依赖本地 Python/Node 环境
- Windows / macOS / Linux 通用
- 热重载：改代码自动生效
- 数据持久化：SQLite volume

### 本机启动

```bash
# 后端 (端口 8000)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端 (端口 3001)
cd frontend
npm install
npm run dev
```

---

## 十、运行模式

| 模式 | 配置 | 说明 |
|------|------|------|
| Mock | `LLM_MODE="mock"` | 默认，零依赖，模板/规则引擎 |
| Live | `LLM_MODE="live"` + API Key | 真 LLM 画像/画布/报告 |
| 报告模式 | `mode=template` / `mode=llm` | 报告可独立选模版/LLM |
| RAG | `RAG_ENABLED="true"` | 向量检索增强，默认关闭 |

---

## 十一、项目进度

| 阶段 | 内容 | 状态 |
|------|------|:---:|
| A — 基础 Demo | FastAPI+Next.js+SQLite+报告导出 | **95%** ✅ |
| B — V2 方法论 | 突破/方向/竞争力/商业终局/方向加权 | **95%** ✅ |
| C — 知识库与质量 | 问题库/分层检索/质量审计/LLM验证 | **90%** ✅ |
| D — 课后跟进 | 30天任务/双周推送/讲师工作台 | **90%** ✅ |
| Docker | docker-compose 一键部署 | **100%** ✅ |
| **整体** | | **~92%** |

---

## 十二、关键文件索引

| 文件 | 说明 |
|------|------|
| `docs/PROJECT_OVERVIEW.md` | 本文档 — 架构与实现总览 |
| `docs/CURRENT_STATUS.md` | 当前状态与测试基准 |
| `docs/PROJECT_SUMMARY_CN.md` | 项目详细总结 |
| `docs/PROJECT_ADVANCEMENT_PLAN.md` | 推进计划 |
| `docs/CODEX_HANDOFF.md` | 开发者交接文档 |
| `docker-compose.yml` | Docker 编排文件 |
| `README.md` | 项目说明与快速开始 |
