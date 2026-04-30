# Meitai AI Business Innovation Agent Demo

当前仓库实现的是一个可运行的咨询式 Demo，用结构化流程帮助企业完成从问卷到课后跟进的完整链路。

## 完整链路

1. 创建企业问卷（支持导入预填）
2. 生成企业画像
3. 商业模式画布 9 格诊断（九要素问题库增强）
4. 突破要素推荐与选择
5. 创新方向延展
6. 差异化竞争力分析
7. 商业终局设计（私域 + 生态 + OPC + 多路径）
8. AI 场景推荐（方向加权）
9. 分层案例匹配（行业→规模→痛点→方向 + 来源标注）
10. 最终报告生成（14 章节 + 质量审计）
11. 报告导出（Markdown / DOCX / 打印版 / PDF）
12. 课后 30 天跟进任务管理
13. 双周案例推送（去重 + 方案再校准）
14. 讲师工作台（分组/批量点评/CSV 导出）

## 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite + ChromaDB（可选）
- **前端**: Next.js 15 + TypeScript + Tailwind CSS
- **AI**: OpenAI 兼容接口（可选，默认 Mock 模式）
- **报告导出**: Markdown / HTML / DOCX

## 目录结构

```
.
├── backend/
│   ├── app/
│   │   ├── api/routes/       # 路由层
│   │   ├── core/             # 配置
│   │   ├── db/               # 数据库
│   │   ├── exporters/        # 导出
│   │   ├── models/           # 数据模型
│   │   ├── prompts/          # LLM 提示词
│   │   ├── rag/              # RAG 检索
│   │   ├── schemas/          # Pydantic Schema
│   │   └── services/         # 业务服务
│   ├── data/                 # SQLite / Chroma
│   ├── tests/                # 测试
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/              # 页面
│       ├── components/       # 组件
│       └── lib/              # API + 类型
├── knowledge/raw/            # 知识库 YAML
│   ├── ai_scenarios.yaml
│   ├── industry_cases.yaml
│   ├── business_canvas.md
│   ├── report_templates.md
│   └── risk_playbook.md
├── scripts/                  # 启动脚本
├── docs/                     # 设计文档
├── .env.example
└── README.md
```

## 快速开始

### 1. 配置环境

```powershell
Copy-Item .env.example .env
```

默认 Mock 模式即可运行，无需 API Key：

```env
LLM_MODE="mock"
```

如需真实 LLM：

```env
LLM_MODE="live"
OPENAI_API_KEY="sk-..."
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_MODEL="gpt-4o-mini"
LLM_REPORT_ENABLED="true"
```

### 2. 安装依赖

后端：

```powershell
cd backend
pip install -r requirements.txt
```

前端：

```powershell
cd frontend
npm install
```

### 3. 启动

后端（端口 8000）：

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

前端（端口 3001）：

```powershell
cd frontend
npm run dev
```

或使用启动脚本：
- `scripts/back_start.bat`
- `scripts/front_start.bat`

### 4. 访问

| 页面 | 地址 |
|------|------|
| 首页 | `http://localhost:3001` |
| 新建问卷（学员/讲师双视角） | `http://localhost:3001/assessment` |
| 指定问卷 | `http://localhost:3001/assessment/{assessment_id}` |
| 报告预览 | `http://localhost:3001/report/{assessment_id}` |
| 课前导入 | `http://localhost:3001/intake` |

## API 端点总览

### 核心流程

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `POST` | `/api/assessments` | 创建问卷 |
| `GET` | `/api/assessments/{id}` | 完整聚合状态 |
| `POST` | `/api/assessments/{id}/profile` | 生成企业画像 |
| `POST` | `/api/assessments/{id}/canvas` | 画布 9 格诊断 |
| `POST` | `/api/assessments/{id}/breakthrough/recommend` | 突破要素推荐 |
| `POST` | `/api/assessments/{id}/breakthrough/select` | 突破要素选择 |
| `POST` | `/api/assessments/{id}/directions/expand` | 方向延展 |
| `POST` | `/api/assessments/{id}/directions/select` | 方向选择 |
| `GET` | `/api/assessments/{id}/directions` | 查看已选方向 |
| `POST` | `/api/assessments/{id}/competitiveness/generate` | 竞争力分析 |
| `GET` | `/api/assessments/{id}/competitiveness` | 查看竞争力 |
| `POST` | `/api/assessments/{id}/endgame/generate` | 商业终局分析 |
| `GET` | `/api/assessments/{id}/endgame` | 查看商业终局 |
| `POST` | `/api/assessments/{id}/scenarios` | 场景推荐 |
| `POST` | `/api/assessments/{id}/cases` | 案例匹配（分层检索） |
| `POST` | `/api/assessments/{id}/report` | 生成报告（模板/LLM） |
| `GET` | `/api/assessments/{id}/report-context` | 报告上下文 |

### 报告与导出

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/reports/{report_id}` | 获取报告详情 |
| `GET` | `/api/reports/{report_id}/export/markdown` | 导出 Markdown |
| `GET` | `/api/reports/{report_id}/export/docx` | 导出 DOCX |
| `GET` | `/api/reports/{report_id}/export/pdf` | 导出 PDF |
| `GET` | `/api/reports/{report_id}/print` | 打印版 HTML |
| `GET` | `/api/reports/{report_id}/enrich` | 报告增强 |
| `GET` | `/api/reports/{report_id}/quality` | 质量审计报告 |
| `POST` | `/api/reports/{report_id}/share` | 生成分享链接 |
| `GET` | `/api/reports/{report_id}/share/{token}` | 访问分享链接 |

### 课后跟进

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/assessments/{id}/follow-up` | 跟进计划 |
| `PATCH` | `/api/assessments/{id}/follow-up/tasks/{task_id}` | 更新任务 |
| `POST` | `/api/assessments/{id}/follow-up/recalibrate` | 复盘修订 |
| `POST` | `/api/assessments/{id}/push` | 双周案例推送 |
| `GET` | `/api/assessments/{id}/push/history` | 推送历史 |
| `POST` | `/api/assessments/{id}/recalibrate` | 再校准方案 |

### 讲师视角

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/instructor/dashboard` | 学员总览 |
| `POST` | `/api/instructor/batch-comment` | 批量点评 |
| `GET` | `/api/instructor/export?format=csv` | 导出 CSV |

### RAG 检索

RAG 默认关闭，路由前缀为 `/rag`（非 `/api/rag`）。

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/rag/status` | RAG 状态 |
| `POST` | `/rag/search` | 搜索知识库 |
| `POST` | `/rag/ingest` | 注入知识 |

## 报告结构

模板报告固定 14 章节：

1. 企业基本画像
2. 当前商业模式画布诊断
3. 突破要素
4. 创新方向延展
5. AI 成熟度评估
6. 高优先级 AI 提效场景
7. 推荐场景详细规划
8. 差异化竞争力设计
9. 参考案例与启示
10. 三阶段 AI 创新路线图
11. 90 天行动计划
12. 风险与阻力
13. 讲师点评区
14. 商业终局设计

## 环境变量参考

```env
APP_NAME="Meitai AI Business Innovation Agent API"
APP_ENV="development"
FRONTEND_ORIGIN="http://localhost:3001"
DATABASE_URL="sqlite:///./backend/data/meitai_demo.db"
LLM_MODE="mock"
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
OPENAI_API_KEY=""
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_MODEL=""
LLM_REPORT_ENABLED="false"
LLM_REPORT_TIMEOUT_SECONDS="60"
RAG_ENABLED="false"
CHROMA_PERSIST_DIR="./backend/data/chroma"
RAG_TOP_K="5"
INTAKE_MAX_UPLOAD_SIZE_MB="10"
INTAKE_PDF_OCR_ENABLED="true"
INTAKE_PDF_OCR_MIN_TEXT_CHARS="20"
INTAKE_PDF_OCR_MAX_PAGES="12"
```

## 测试

后端：

```powershell
cd backend
python -m pytest tests/ -v
# 19 passed, 1 skipped
```

前端：

```powershell
cd frontend
npx vitest run
# 6 passed
```

E2E 全链路：

```powershell
cd backend
python -m pytest tests/test_e2e_full_chain.py -v -s
# 26 个步骤验证，涵盖画像→画布→突破→方向→竞争力→商业终局→
#   场景→案例→报告→导出→分享→跟进→推送→讲师工作台→级联清空
```

## 端口说明

| 服务 | 端口 | 说明 |
|------|:---:|------|
| 前端 | **3001** | 默认端口（3000 已保留） |
| 后端 | **8000** | FastAPI 开发服务器 |

## 运行模式

- **Mock 模式**（默认）：`LLM_MODE="mock"`，所有生成走模板 / 规则引擎，无需 API Key
- **Live 模式**：`LLM_MODE="live"`，画像、画布、报告可走真实 LLM
- **报告模式**：报告支持 `mode=template`（始终模板）、`mode=llm`（尝试 LLM，失败回退）
