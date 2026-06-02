# AGENTS.md

## Project Overview

This repository implements the "Meitai AI Business Innovation Agent" demo: a runnable consulting workflow that helps executives move from pre-class intake to AI business innovation planning, report generation, and post-class follow-up.

The current product flow includes:
- pre-class intake import and company assessment
- company profile generation
- business model canvas diagnosis
- breakthrough factor recommendation and selection
- innovation direction expansion and selection
- differentiated competitiveness analysis
- business endgame design
- AI scenario recommendation
- hierarchical case matching with source notes
- 14-section final report generation and quality review
- Markdown, DOCX, printable HTML, and PDF export
- 30-day follow-up task management
- biweekly case push and recalibration
- instructor dashboard, batch comments, and CSV export

## Tech Stack

- Backend: FastAPI + SQLAlchemy + SQLite + optional ChromaDB
- Frontend: Next.js 15.5 + React 18.2 + TypeScript + Tailwind CSS
- AI: OpenAI-compatible API, defaulting to mock mode
- Runtime expectation: conda env `meitai-project`, Python 3.11

## Ports

- Frontend: `3001` by default. Do not change it to `3000`.
- Backend: `8000` by default.
- Some startup scripts can auto-fallback to another free port.

## Common Commands

```powershell
# One-click local start from repo root
.\start.bat

# Backend
cd backend
conda activate meitai-project
python run.py

# Backend with fixed port
cd backend
conda activate meitai-project
python -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Local Command Rules

- Never use `rg` / `ripgrep` in this repository. It is blocked in this local Windows environment and may fail with `Access is denied`.
- Use PowerShell-native alternatives instead:
  - File search: `Get-ChildItem -Recurse`
  - Text search: `Select-String`
  - File reading: `Get-Content`
- Do not stop the task just because `rg` is unavailable; switch directly to the PowerShell-native commands above.

## Checks

Run the narrowest useful checks for the files changed.

Backend tests must always run through the Anaconda environment `meitai-project`.
Prefer `conda run -n meitai-project ...` so tests do not accidentally use the global Python environment.

```powershell
# Backend tests
cd backend
conda run -n meitai-project python -m pytest tests/ -v

# Full-chain backend test
cd backend
conda run -n meitai-project python -m pytest tests/test_e2e_full_chain.py -v -s

# Frontend checks
cd frontend
npm run typecheck
npm run test
npm run build
```

## Key Directories

```text
backend/app/api/routes/  API routes
backend/app/core/        config, LLM client, optional mykey.py loading
backend/app/db/          database session and setup
backend/app/exporters/   report exporters
backend/app/models/      SQLAlchemy models
backend/app/prompts/     LLM prompts
backend/app/rag/         optional RAG retrieval
backend/app/schemas/     Pydantic schemas
backend/app/services/    business logic
backend/data/            local SQLite and Chroma data, gitignored
backend/exports/         generated exports, gitignored
backend/tests/           backend test suite

frontend/src/app/        Next.js pages and routes
frontend/src/components/ React components and component tests
frontend/src/lib/        API client, shared types, utilities

knowledge/raw/           source YAML/Markdown knowledge base
scripts/                 startup and utility scripts
docs/                    architecture, status, and design docs
```

## Important API Areas

- Core assessment flow: `/api/assessments`
- Profile, canvas, breakthrough, directions, competitiveness, endgame, scenarios, cases, report context: under `/api/assessments/{id}/...`
- Reports and exports: `/api/reports/{report_id}/...`
- Follow-up, push, recalibration: under `/api/assessments/{id}/...`
- Instructor workflows: `/api/instructor/...`
- RAG routes use `/rag`, not `/api/rag`

Check `README.md` and `使用方法.md` for the full current endpoint list before adding or changing API behavior.

## Environment Rules

- Default mode is mock: `LLM_MODE="mock"`.
- Live mode uses `LLM_MODE="live"` with `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL`.
- `.env` values override `backend/app/core/mykey.py`; both override config defaults.
- `mykey.py` is local secret configuration and must not be committed.
- Keep `RAG_ENABLED=false` by default.
- Keep `LLM_REPORT_ENABLED=false` by default unless the user explicitly wants live LLM reports.

## Report Rules

- Preserve template report generation.
- Preserve LLM-to-template fallback behavior.
- Template reports are the deterministic baseline and should work without an API key.
- The final report structure currently has 14 sections; do not remove sections casually.
- Export paths include Markdown, DOCX, printable HTML, and PDF.

## Constraints

- Do not commit `.env`, `backend/app/core/mykey.py`, SQLite databases, Chroma stores, generated exports, `.next`, `node_modules`, or test caches.
- Do not stage, commit, or push changes from these protected paths unless the user explicitly overrides this rule in the same turn:
  - `docs/`
  - `.claude/`
  - `plans/`
  - `规划.docx`
  - `使用方法.md`
  - `使用说明.md`
  - `CLAUDE.md`
  - `docker-compose.yml`
  - `mykey.py.example`
- Before every commit or push, run `git status` and make sure none of the protected paths above are staged.
- Do not refactor the project structure unless the user explicitly asks.
- Do not introduce a new state management library or UI framework without a clear request.
- Prefer existing service, schema, route, and component patterns.
- Keep RAG optional and disabled by default.
- Keep frontend port conventions intact.

## Before Finishing

Summarize:
- files changed
- behavior or documentation updated
- commands/checks run
- anything not verified
