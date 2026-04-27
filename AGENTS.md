# AGENTS.md

## Project Goal

This repository implements a demo system called "Meitai AI Business Innovation Agent".

The system helps business executives generate AI business innovation plans through:
- guided company assessment
- business model canvas diagnosis
- AI scenario recommendation
- case matching
- report generation (template or LLM-enhanced)

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS
- **AI**: OpenAI-compatible LLM API (configurable)
- **RAG**: ChromaDB for case knowledge retrieval (optional)

## Port Conventions

- **Frontend**: 3001 (NOT 3000 - hardcoded in package.json)
- **Backend**: 8000

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev  # runs on port 3001
```

## Key Directories

```
backend/
├── app/
│   ├── api/routes/       # API endpoints
│   ├── core/             # Config, LLM client
│   ├── db/               # Database session
│   ├── models/           # SQLAlchemy models
│   ├── prompts/          # LLM prompts (NEW)
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic
├── data/
│   ├── meitai_demo.db    # SQLite database
│   └── chroma/           # RAG vector store
└── requirements.txt

frontend/
├── src/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   └── lib/              # API client, types
└── package.json          # port 3001 configured
```

## Key API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/assessments` | Create assessment |
| GET | `/api/assessments/{id}` | Get assessment detail |
| POST | `/api/assessments/{id}/canvas` | Save canvas data |
| POST | `/api/assessments/{id}/scenarios` | Generate scenario recommendations |
| POST | `/api/assessments/{id}/report?mode=template\|llm` | Generate report |
| GET | `/api/reports/{id}` | Get report detail |
| GET | `/api/reports/{id}/export/markdown` | Export as markdown |
| GET | `/api/reports/{id}/export/docx` | Export as docx |
| POST | `/api/rag/search` | RAG search (optional) |

## Environment Variables

```bash
# Core
APP_ENV=development
DATABASE_URL=sqlite:///./backend/data/meitai_demo.db

# LLM (required for LLM mode)
LLM_MODE=openai|mock
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# RAG (optional, disabled by default)
RAG_ENABLED=false
CHROMA_PERSIST_DIR=./backend/data/chroma
RAG_TOP_K=5

# LLM Report (optional, disabled by default)
LLM_REPORT_ENABLED=false
LLM_REPORT_TIMEOUT_SECONDS=60
```

## Report Generation Modes

1. **Template Mode (default)**: Fast, deterministic, no LLM required
2. **LLM Mode (optional)**: Uses LLM for enhanced, personalized reports
   - Requires `LLM_REPORT_ENABLED=true` and valid `OPENAI_API_KEY`
   - Falls back to template mode if LLM unavailable

## Important Constraints

- **DO NOT** delete or modify existing template report functionality
- **DO NOT** remove fallback to template mode
- **DO NOT** change port from 3001 to 3000
- **DO NOT** enable RAG by default
- **DO NOT** refactor project structure

## Before Finishing a Task

Summarize:
- files changed
- features implemented
- how to run
- checks performed
- known limitations