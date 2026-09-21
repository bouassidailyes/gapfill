# AI Student Scheduler

Hackathon app: upload a student `.ics`, paste a to-do list, get a planned week (calendar UI + downloadable `.ics`).

The LLM proposes; code guarantees. Design: [`architecture.md`](architecture.md).

## Prerequisites

- Python 3.11+
- Node 20+

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy ..\.env.example .env   # or: cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

`GET http://localhost:8000/api/health` → `{"ok":true}`

Set `ANTHROPIC_API_KEY` in `.env`. `DEMO_MODE=1` skips the LLM and returns `fixtures/schedule.mock.json`.

### Frontend

```bash
cd frontend
npm install
# mock week without a live backend:
# Windows: set VITE_USE_MOCK=1
# macOS/Linux: VITE_USE_MOCK=1
npm run dev
```

Vite proxies `/api` → `http://localhost:8000`. Open the URL Vite prints (usually `http://localhost:5173`).

## Fixtures

| File | What |
|---|---|
| `fixtures/sample_calendar.ics` | Sample week (recurring + all-day + two locations) |
| `fixtures/sample_tasks.txt` | 8 free-text tasks |
| `fixtures/settings.json` | Default settings |
| `fixtures/schedule.mock.json` | Hand-written planned week |
| `fixtures/allocation.mock.json` | Hand-written task plans |

## Smoke test

```bash
cd backend && pytest -q
curl -s http://localhost:8000/api/health
cd frontend && npm run build
```
