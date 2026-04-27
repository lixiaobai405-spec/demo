# Next Task: 5C-1 LLM Report Verification

## Objective

Verify and complete the LLM report generation feature with proper fallback handling and metadata display.

## Sub-tasks

### 1. LLM Output Self-Check
**File**: `backend/app/services/llm_report_writer.py`

- [ ] Add validation for all 11 required sections
- [ ] Check for placeholder content (未补充, 待填写)
- [ ] Validate JSON structure before parsing
- [ ] Log warnings for missing/weak content

### 2. Report Metadata Display
**File**: `frontend/src/components/report-document-viewer.tsx`

- [ ] Show `used_llm` badge (LLM增强/模板生成)
- [ ] Show `used_rag` badge if RAG was used
- [ ] Display `warnings` array to user
- [ ] Add to print/export views

### 3. Fallback Verification
**File**: `backend/app/services/report_service.py`

- [ ] Test fallback when `LLM_REPORT_ENABLED=false`
- [ ] Test fallback when `OPENAI_API_KEY` missing
- [ ] Test fallback on LLM timeout
- [ ] Test fallback on LLM error
- [ ] Ensure `used_llm=false` in metadata when fallback

### 4. Live Testing
- [ ] Start backend with `LLM_REPORT_ENABLED=true`
- [ ] Create assessment through UI
- [ ] Complete canvas
- [ ] Generate report with mode=llm
- [ ] Verify metadata shows `used_llm=true`
- [ ] Test fallback scenario

## Acceptance Criteria

1. ✅ LLM mode produces valid 11-section report
2. ✅ Template mode still works when LLM disabled
3. ✅ Metadata correctly shows generation mode
4. ✅ Warnings displayed to user
5. ✅ No 500 errors on LLM failure

## Test Commands

```bash
# Test LLM mode
curl -X POST "http://localhost:8000/api/assessments/{id}/report?mode=llm"

# Test template fallback
curl -X POST "http://localhost:8000/api/assessments/{id}/report?mode=template"

# Check report metadata
curl http://localhost:8000/api/reports/{report_id}
```

## Files to Modify

1. `backend/app/services/llm_report_writer.py` - Add validation
2. `backend/app/services/report_service.py` - Enhance fallback logic
3. `frontend/src/components/report-document-viewer.tsx` - Show metadata
4. `frontend/src/lib/types.ts` - Ensure ReportDocumentResponse has metadata fields

## Constraints

- DO NOT break template report generation
- DO NOT require LLM_API_KEY for basic functionality
- DO NOT change existing API response structure
- ALWAYS set used_llm=false when using template fallback