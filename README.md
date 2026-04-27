# Meitai AI Business Innovation Agent Demo

当前仓库实现的是一个可运行的咨询式 Demo，用结构化流程帮助企业完成：

1. 创建企业问卷
2. 生成企业画像
3. 生成商业模式画布 9 格诊断
4. 生成 Top 3 AI 场景推荐
5. 匹配匿名行业参考案例
6. 生成最终报告预览

当前阶段不包含：

- Word / PDF 导出

## 当前能力

- FastAPI 后端
- Next.js + TypeScript + Tailwind 前端
- SQLite 持久化 Assessment、企业画像、商业画布、场景推荐、案例匹配、最终报告
- 页面刷新后按 `assessment_id` 恢复历史状态
- 报告上下文聚合接口
- 基于本地 YAML 的规则评分场景推荐
- 基于行业、痛点、画布格子和推荐场景的案例匹配
- 最终报告结构化预览页

## 目录结构

```text
.
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ models/
│  │  ├─ schemas/
│  │  └─ services/
│  ├─ data/
│  └─ requirements.txt
├─ frontend/
│  └─ src/
│     ├─ app/
│     ├─ components/
│     └─ lib/
├─ knowledge/
│  └─ raw/
│     ├─ ai_scenarios.yaml
│     └─ industry_cases.yaml
├─ scripts/
│  ├─ back_start.bat
│  └─ front_start.bat
├─ .env.example
└─ README.md
```

## 环境变量

先复制模板：

```powershell
cd E:\company_work\3
Copy-Item .env.example .env
```

默认推荐使用 `mock` 模式：

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
```

如果要接真实模型，把 `.env` 改成：

```env
LLM_MODE="live"
OPENAI_API_KEY="你自己的 key"
OPENAI_BASE_URL="你的 OpenAI 兼容接口地址"
OPENAI_MODEL="你自己的模型名"
```

说明：

- 企业画像和商业画布支持 `mock / live`
- 场景推荐固定走本地规则评分
- 案例匹配固定走规则评分
- 当前最终报告为模板化结构化报告预览，不做导出
- SQLite 默认文件在 [backend/data/meitai_demo.db](E:\company_work\3\backend\data\meitai_demo.db)

## 本地启动

### 方式一：命令行启动

后端：

```powershell
cd E:\company_work\3
E:\Anaconda3\envs\rag-env\python.exe -m pip install -r backend\requirements.txt
E:\Anaconda3\envs\rag-env\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

前端：

```powershell
cd E:\company_work\3\frontend
npm install
npm run dev
```

### 方式二：bat 启动

- [scripts/back_start.bat](E:\company_work\3\scripts\back_start.bat)
- [scripts/front_start.bat](E:\company_work\3\scripts\front_start.bat)

说明：

- 后端脚本固定使用 `E:\Anaconda3\envs\rag-env\python.exe`
- 前端脚本会先检查 `frontend/node_modules`，不存在时自动执行一次 `npm install`

## 页面地址

本项目默认端口：
- **Frontend**: http://localhost:3001
- **Backend**: http://localhost:8000

> 注意：3000端口已保留给其他项目，本项目不使用3000作为默认端口。

页面地址：
- 首页：`http://localhost:3001`
- 新建问卷：`http://localhost:3001/assessment`
- 指定问卷回看：`http://localhost:3001/assessment/{assessment_id}`
- 报告上下文页：`http://localhost:3001/report-context/{assessment_id}`
- 最终报告预览页：`http://localhost:3001/report/{assessment_id}`

## API

### `GET /health`

健康检查。

### `POST /api/assessments`

创建企业问卷记录。

### `GET /api/assessments/{assessment_id}`

返回一个 Assessment 的完整聚合状态：

- `assessment`
- `company_profile`
- `canvas_diagnosis`
- `scenario_recommendation`
- `case_recommendation`
- `generated_report`
- `progress`

### `POST /api/assessments/{assessment_id}/profile`

生成并保存企业画像。

### `POST /api/assessments/{assessment_id}/canvas`

生成并保存商业模式画布 9 格诊断。

### `POST /api/assessments/{assessment_id}/scenarios`

生成并保存 Top 3 AI 场景推荐。

兼容旧别名：

- `POST /api/assessments/{assessment_id}/scenario-recommendations`

### `POST /api/assessments/{assessment_id}/cases`

根据行业、痛点、商业画布和推荐场景，匹配匿名行业参考案例并保存结果。

### `POST /api/assessments/{assessment_id}/report`

基于画像、画布、场景推荐和案例结果，生成并保存最终报告预览。

### `GET /api/assessments/{assessment_id}/report-context`

只聚合报告生成所需上下文，不生成最终报告。

## 当前知识库

场景库：

- [knowledge/raw/ai_scenarios.yaml](E:\company_work\3\knowledge\raw\ai_scenarios.yaml)

案例库：

- [knowledge/raw/industry_cases.yaml](E:\company_work\3\knowledge\raw\industry_cases.yaml)

说明：

- `ai_scenarios.yaml` 提供 AI 场景定义和规则评分字段
- `industry_cases.yaml` 提供匿名行业参考案例和匹配字段

## 前端健康检查失败排查

如果前端页面显示"健康检查失败"，按以下步骤排查：

1. **查看前端实际端口**
   - 前端默认运行在 3000 端口
   - 如果 3000 被占用，Next.js 可能自动切换到 3001
   - 检查终端输出的实际端口

2. **确认后端 CORS 配置**
   - 检查 `backend/app/main.py` 的 `allow_origins` 是否包含前端实际端口
   - 当前已配置：`localhost:3000`、`localhost:3001`、`127.0.0.1:3000`、`127.0.0.1:3001`

3. **确认环境变量正确**
   - 检查 `.env.local` 或 `.env` 中的 `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
   - 修改 `.env.local` 后需要重启前端

4. **确认后端运行**
   - 访问 `http://localhost:8000/health` 应返回 `{"status":"ok",...}`
   - 如果无响应，检查后端进程是否在运行

5. **手动测试 CORS**
   ```powershell
   curl.exe -i -H "Origin: http://localhost:3001" http://localhost:8000/health
   ```
   返回头应包含：`access-control-allow-origin: http://localhost:3001`

## 持久化与回看

当前已持久化：

- 企业问卷：`Assessment`
- 企业画像：存储在 `Assessment.profile_payload`
- 商业画布：`CanvasDiagnosis`
- 场景推荐：`ScenarioRecommendation`
- 案例匹配：`CaseRecommendation`
- 最终报告：`GeneratedReport`

前端会根据 URL 中的 `assessment_id` 调用：

- `GET /api/assessments/{assessment_id}`

恢复以下内容：

- 企业问卷输入
- 企业画像结果
- 商业画布结果
- Top 3 场景推荐
- 匿名行业案例匹配结果
- 最终报告预览
- 当前流程进度

## 已完成检查

- `E:\Anaconda3\envs\rag-env\python.exe -m compileall backend\app`
- `cd E:\company_work\3\frontend && npm run build`
- 后端链路验证：
  - 创建 assessment
  - 生成 profile
  - 生成 canvas
  - 生成 scenarios
  - 生成 cases
  - 生成 report
  - 获取 assessment 聚合状态
  - 验证缺少前置结果时 `/cases` 和 `/report` 返回清晰错误

## RAG 知识库检索

### 配置说明

RAG（检索增强生成）模块默认关闭。启用需要以下步骤：

1. **配置环境变量**（在 `.env` 或 `.env.local` 中）：
   ```bash
   RAG_ENABLED=true
   OPENAI_API_KEY=your-api-key  # 可选，无则使用mock
   CHROMA_PERSIST_DIR=./chroma_db
   RAG_TOP_K=5
   ```

2. **注入知识库**：
   ```bash
   cd backend
   python scripts/ingest_knowledge.py
   ```

3. **验证状态**：
   ```bash
   curl http://localhost:8000/api/rag/status
   ```

### Mock Embedding 模式

当未配置 `OPENAI_API_KEY` 时，系统自动降级为 Mock Embedding：

- 返回随机向量，仅用于 Demo 演示
- 检索结果不可靠，不应用于生产
- API 返回 `is_mock_embedding: true` 和 `warning` 字段提示

### API 端点

| 端点 | 说明 |
|------|------|
| `GET /api/rag/status` | 获取 RAG 状态（含 mock 标记） |
| `POST /api/rag/search` | 搜索知识库 |
| `POST /api/rag/ingest` | 注入知识 |

### 分数计算

Hybrid 检索分数归一化：
- `rule_score`: 规则匹配分（0-100）
- `vector_score`: 向量相似度（0-1）
- `vector_score_normalized`: 归一化向量分（0-100）
- `final_score = rule_score × 0.70 + vector_score_normalized × 0.30`

## 已知限制

- Word / PDF 导出尚未实现
- 最终报告目前为模板化结构，不是富文本排版版式
- 场景推荐与案例匹配都已规则化，但还可以继续细化行业权重
- 当前没有完整自动化测试框架，只做了关键链路验证

## 下一步建议

进入下一阶段时，建议按这个顺序推进：

1. 在报告结果之上增加 Markdown / HTML 版式输出
2. 细化 RAG 知识库内容，提升报告论据质量
3. 在报告稳定后补 Word / PDF 导出
4. 最后再补更细的权限、日志、审计与测试覆盖
