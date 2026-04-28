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

## Recently Completed

### Task 5C-1 / A2: LLM Report Verification and Export Acceptance ✅
- [x] LLM output self-check validation
- [x] Report metadata display (`used_llm`, `used_rag`, `warnings`)
- [x] Fallback verification when LLM unavailable / timeout / error
- [x] Live end-to-end report generation verification
- [x] Markdown / DOCX / print export verification under real LLM report

### Latest Acceptance Record
- Real LLM report record verified with `generation_mode=llm` and `used_llm=true`
- `GET /api/reports/{report_id}/export/markdown` returns `200` and includes metadata header
- `GET /api/reports/{report_id}/export/docx` returns `200` with downloadable DOCX attachment
- `GET /api/reports/{report_id}/print` returns `200` and print HTML contains `used_llm=true`
- Backend health check remains normal during export verification

## In Progress

### Task 5C-2 / A3: Main Flow Automated Tests (NEXT)
- [ ] Add backend integration test scaffold
- [ ] Cover questionnaire -> profile -> canvas -> scenarios -> cases -> report
- [ ] Cover template mode and LLM fallback mode
- [ ] Cover report export endpoints
- [ ] Cover prerequisite / error-path assertions

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
| LLM Report | ✅ Verified | Fallback and metadata verified |
| RAG Search | ⚠️ Disabled | Optional feature |
| Export (MD/DOCX) | ✅ Verified | Real LLM report export passed |

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
| LLM_MODE | mock | Set to `live` for real profile/canvas generation |
| OPENAI_API_KEY | empty | Required for LLM mode |
| LLM_REPORT_ENABLED | false | Set to `true` for real LLM report writing |
| FRONTEND_ORIGIN | `http://localhost:3001` | Keep aligned with frontend dev port |
| RAG_ENABLED | false | Leave disabled |

## Consistency Notes

- Frontend dev port is `3001`, not `3000`
- `.env.example` uses `FRONTEND_ORIGIN=http://localhost:3001`
- RAG routes use `/rag/*`, not `/api/rag/*`
- DOCX export is implemented; PDF export is not implemented yet
- Real profile/canvas LLM uses `LLM_MODE=live`; report LLM additionally requires `LLM_REPORT_ENABLED=true`
