# Current Status

## Completed Tasks

### Task 1-4: Core System ✅
- [x] Project setup (FastAPI + Next.js)
- [x] Database models and migrations
- [x] Assessment flow (questionnaire + progress tracking)
- [x] Business Canvas grid (9 blocks with validation)

### Task 5A: Scenario Recommendation ✅
- [x] Rule-based scenario scoring from YAML rules
- [x] LLM-enhanced scenario generation
- [x] Top-3 scenario recommendations API

### Task 5B: Case Matching ✅
- [x] Similarity-based case matching
- [x] Integration with assessment data
- [x] Case data loading from YAML

### Task 5C: Report Generation ✅
- [x] Template-based report (11 sections, always works)
- [x] LLM-enhanced report (optional, requires API key)
- [x] Frontend mode selector (template/LLM)
- [x] Export to Markdown and DOCX
- [x] Report context aggregation API

## In Progress

### Task 5C-1: LLM Report Verification (NEXT)
- [ ] LLM output self-check validation
- [ ] Report metadata display (used_llm, used_rag, warnings)
- [ ] Fallback verification when LLM unavailable
- [ ] Live end-to-end testing

## Not Started

### Task 6: Polish & Demo Prep
- [ ] UI/UX refinements
- [ ] Error handling improvements
- [ ] Demo data preparation
- [ ] Documentation finalization

## Feature Status Matrix

| Feature | Status | Notes |
|---------|--------|-------|
| Assessment Creation | ✅ Done | Full CRUD |
| Canvas Editor | ✅ Done | 9-block grid |
| Scenario Recommendation | ✅ Done | Rule + LLM |
| Case Matching | ✅ Done | Similarity-based |
| Template Report | ✅ Done | Always available |
| LLM Report | ⚠️ Needs Testing | Fallback required |
| RAG Search | ⚠️ Disabled | Optional feature |
| Export (MD/DOCX) | ✅ Done | Both formats |

## Database Schema Status

All models auto-created via `create_all()`:
- Assessment ✅
- BusinessCanvas ✅
- ScenarioRecommendation ✅
- MatchedCase ✅
- GeneratedReport ✅ (with used_llm, used_rag, warnings fields)

## Configuration Status

| Env Var | Default | Current Needed |
|---------|---------|----------------|
| LLM_MODE | mock | Set to `openai` for real LLM |
| OPENAI_API_KEY | empty | Required for LLM mode |
| LLM_REPORT_ENABLED | false | Set to `true` for LLM reports |
| FRONTEND_ORIGIN | `http://localhost:3001` | Keep aligned with frontend dev port |
| RAG_ENABLED | false | Leave disabled |

## Consistency Notes

- Frontend dev port is `3001`, not `3000`
- `.env.example` uses `FRONTEND_ORIGIN=http://localhost:3001`
- RAG routes use `/rag/*`, not `/api/rag/*`
- DOCX export is implemented; PDF export is not implemented yet
