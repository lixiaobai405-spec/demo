# CODEX Handoff Document

## Project Overview

**Meitai AI Business Innovation Agent** - A demo system helping business executives generate AI innovation plans through guided assessment, canvas diagnosis, scenario recommendations, and report generation.

## Current State Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Assessment Flow | ✅ Complete | Multi-step questionnaire |
| Business Canvas | ✅ Complete | Interactive grid editor |
| Scenario Recommendation | ✅ Complete | Rule-based + LLM enhancement |
| Case Matching | ✅ Complete | Similarity-based matching |
| Template Report | ✅ Complete | 11-section structured output |
| LLM Report | ✅ Implemented | Optional enhancement mode |
| RAG Integration | ⚠️ Implemented | Disabled by default |

## Key Files to Understand

### Backend Core
- `backend/app/core/config.py` - All settings and env vars
- `backend/app/core/llm_client.py` - LLM API client
- `backend/app/api/routes/assessments.py` - Main API endpoints
- `backend/app/services/report_service.py` - Report generation logic
- `backend/app/services/llm_report_writer.py` - LLM-enhanced reports
- `backend/app/prompts/report_writer_prompt.py` - LLM prompt template

### Frontend Core
- `frontend/src/app/page.tsx` - Home page
- `frontend/src/app/assessment/[assessmentId]/page.tsx` - Assessment flow
- `frontend/src/app/report/[assessmentId]/page.tsx` - Report generation
- `frontend/src/components/report-preview-viewer.tsx` - Report mode selector
- `frontend/src/lib/api.ts` - API client

### Database
- `backend/app/models/` - All SQLAlchemy models
- `backend/app/db/session.py` - Database initialization

## Running the Project

```bash
# Terminal 1: Backend
cd E:\company_work\3\backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd E:\company_work\3\frontend
npm run dev
# Opens at http://localhost:3001
```

## Testing Commands

```bash
# Backend health check
curl http://localhost:8000/api/health

# Test assessment creation
curl -X POST http://localhost:8000/api/assessments -H "Content-Type: application/json" -d "{\"company_name\": \"Test\", \"industry\": \"Tech\", \"contact\": \"test@test.com\"}"

# Test template report generation
curl -X POST "http://localhost:8000/api/assessments/{id}/report?mode=template"

# Test LLM report generation (requires OPENAI_API_KEY)
curl -X POST "http://localhost:8000/api/assessments/{id}/report?mode=llm"
```

## Important Notes for Codex

1. **Frontend Port**: Always use 3001, never 3000
2. **Template Report**: Must always work, never break it
3. **LLM Report**: Optional enhancement, requires fallback
4. **RAG**: Disabled by default, don't force enable
5. **Database**: Uses SQLite, auto-creates on first run
6. **No Refactoring**: Do not change project structure

## Known Issues

- RAG search requires pre-populated ChromaDB
- LLM report may timeout for large inputs
- Export functions need valid report ID