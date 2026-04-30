# CODEX Handoff Document

## Project Overview

**Meitai AI Business Innovation Agent** — 帮助企业高管通过引导式评估、画布诊断、场景推荐和报告生成来制定 AI 创新方案的 Demo 系统。

## Current State Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Assessment Flow | ✅ Complete | 14-step full-chain |
| Business Canvas | ✅ Complete | 9-block + problem library |
| Breakthrough | ✅ Complete | 9-element scoring + selection |
| Direction Expansion | ✅ Complete | 6 directions per element |
| Competitiveness | ✅ Complete | VP reconstruction + chain |
| Endgame Design | ✅ Complete | Private Domain + Ecosystem + OPC |
| Scenario Recommendation | ✅ Complete | Rule-based + direction-weighted |
| Case Matching | ✅ Complete | Layered retrieval + source annotation |
| Template Report | ✅ Complete | 14-section with quality audit |
| LLM Report | ✅ Implemented | Optional enhancement + fallback |
| Export | ✅ Complete | MD/DOCX/Print/PDF |
| Follow-Up | ✅ Complete | 30-day task tracking + push |
| Instructor Dashboard | ✅ Complete | Batch comment + CSV export |
| RAG Integration | ⚠️ Disabled | Optional, prefix `/rag` |

## Key Files

### Backend
- `backend/app/core/config.py` — 环境配置
- `backend/app/api/routes/assessments.py` — 主 API
- `backend/app/api/router.py` — 路由注册
- `backend/app/services/llm_client.py` — LLM 客户端
- `backend/app/services/report_builder.py` — 报告模板构建
- `backend/app/services/case_matcher.py` + `layered_retriever.py` — 案例匹配
- `backend/app/services/quality_checker.py` — 质量审计
- `backend/app/services/follow_up_service.py` + `push_service.py` — 课后跟进
- `backend/app/services/instructor_service.py` — 讲师工作台
- `backend/app/schemas/canvas_problems.py` — 九要素问题库
- `backend/app/prompts/report_writer_prompt.py` — LLM 提示词

### Frontend
- `frontend/src/app/page.tsx` — 首页
- `frontend/src/app/assessment/page.tsx` — 学员/讲师双视角
- `frontend/src/app/report/[assessmentId]/page.tsx` — 报告预览
- `frontend/src/app/intake/page.tsx` — 课前导入
- `frontend/src/components/assessment-workbench.tsx` — 学员工作台
- `frontend/src/components/instructor-dashboard.tsx` — 讲师仪表盘
- `frontend/src/components/follow-up-dashboard.tsx` — 跟进面板
- `frontend/src/components/push-panel.tsx` — 推送面板
- `frontend/src/lib/api.ts` + `types.ts` — API 客户端 + 类型

### Database
- `backend/app/models/` — 11 个数据模型
- `backend/app/db/session.py` — 数据库初始化

## Running

```bash
# Backend (port 8000)
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend (port 3001)
cd frontend
npm install
npm run dev
```

Or use: `scripts/back_start.bat` + `scripts/front_start.bat`

## Testing

```bash
cd backend
python -m pytest tests/ -v     # 19 passed, 1 skipped
python -m pytest tests/test_e2e_full_chain.py -v -s  # 26-step E2E

cd frontend
npx vitest run                  # 6 passed
```

## Ports

| Service | Port |
|---------|:---:|
| Frontend | **3001** |
| Backend | **8000** |
