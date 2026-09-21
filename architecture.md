# AI Student Scheduler — Architecture


## 1. What we're building

**Input:** an `.ics` calendar + a free-text to-do list + a few settings (locations, cooking frequency, lost time, free time).
**Output:** a planned week rendered in a calendar UI, downloadable as `.ics`, with the ability to add/remove tasks.

## 2. Principles

1. **The LLM proposes, code guarantees.** Two LLM calls (as specced), but every LLM output is validated by deterministic code. If validation fails: one retry, then a greedy fallback. The demo must never show an invalid calendar.
2. **Constraints are code, not prompts.** Meals, cooking, travel, sleep, free time and lost time are computed deterministically *before* the LLM sees anything. The LLM only sees what is actually free.
3. **Stateless backend, stateful frontend.** No database, no auth. The frontend holds events/tasks/settings/blocks (plus `localStorage` for persistence).
4. **Contracts first, mocks second.** Schemas are frozen at H0:30. Frontend works against `fixtures/schedule.mock.json` until the real backend is ready.
5. **Ownership by directory.** Two Cursor instances = two people editing at once. `backend/` = A, `frontend/` = B, `backend/app/prompts/` + `fixtures/` + `docs/` = C. No cross-directory edits without a heads-up.

## 3. Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.11, FastAPI, pydantic v2, uvicorn | fast to write, typed contracts, great Cursor output |
| ICS | `icalendar` + `recurring-ical-events` | parsing, recurring events (RRULE), export |
| LLM | `anthropic` SDK behind `llm.py` (model via `LLM_MODEL` env, default `claude-sonnet-5`) | one file to change if the hackathon supplies another provider/key |
| Frontend | Vite + React + TypeScript | zero-config |
| Calendar UI | FullCalendar (`@fullcalendar/react`, `timegrid`, `daygrid`, `interaction`) | week view, colors, click/drag out of the box |
| Styling | Tailwind or plain CSS | whichever B prefers |
| Run | `uvicorn` on :8000, Vite dev server proxying `/api` → :8000 | no deployment; demo on localhost |

Env vars: `ANTHROPIC_API_KEY`, `LLM_MODEL`, `DEMO_MODE` (1 = return fixtures, no LLM call).

## 4. Repo layout

```
/
├─ architecture.md · plan.md · tasks.md · README.md
├─ backend/
│  ├─ app/
│  │  ├─ main.py          # FastAPI routes
│  │  ├─ models.py        # pydantic schemas = source of truth (owner: A)
│  │  ├─ ics_parse.py     # .ics -> Event[]
│  │  ├─ constraints.py   # settings -> FixedBlock[] + FreeWindow[]
│  │  ├─ llm.py           # call_json(): call, parse, validate, retry once
│  │  ├─ allocate.py      # LLM call 1
│  │  ├─ place.py         # LLM call 2
│  │  ├─ validate.py      # checks, repair, greedy fallback
│  │  ├─ ics_export.py    # Block[] -> .ics bytes
│  │  └─ prompts/         # allocate.md, place.md (owner: C)
│  └─ tests/
├─ frontend/
│  └─ src/ types.ts (mirror of models.py, owner: B) · api.ts · App.tsx · components/
├─ fixtures/              # sample_calendar.ics, sample_tasks.txt, settings.json,
│                         # allocation.mock.json, schedule.mock.json (owner: C)
└─ docs/                  # demo script, slides, bug list (owner: C)
```

## 5. Pipeline (backend)

```
 .ics ──► [1 parse] ──► Event[] ─────────────┐
 Settings ─► [2 constraints] ─► FixedBlock[] ─┼─► FreeWindow[]  (per day, minus lost-time slack)
                                              │
 Tasks (free text) ─► [3 LLM CALL 1: allocate] ─► TaskPlan[] (sessions with minutes)
                                              │
 FreeWindow[] + TaskPlan[] ─► [4 LLM CALL 2: place] ─► Placement[]
                                              │
 Placement[] ─► [5 validate / retry / greedy fallback] ─► Block[] ─► UI + .ics
```

### Step 1 — Parse ICS (`ics_parse.py`)
- Read with `icalendar`; expand recurring events over the horizon with `recurring-ical-events`.
- Handle date-only (all-day) and datetime events; normalise to the settings timezone (`Europe/Amsterdam`).
- Output `Event {id, title, start, end, location?}`. Bad file → HTTP 422 with a readable message.

### Step 2 — Constraints (`constraints.py`, no LLM)
Build `FixedBlock[]` on top of the events, then compute `FreeWindow[]` = waking hours − events − fixed blocks.

| Constraint | Rule |
|---|---|
| Sleep / waking hours | Only `day_start`–`day_end` is plannable. |
| Meals | For each meal (`lunch`, `dinner`, optional `breakfast`): put a block of `minutes` at the earliest gap inside its window that doesn't overlap an event. Window fully busy → warning. |
| Cooking | `mode: "daily"` → a cook block just before dinner. `"batch"` → `batch_per_week` long cook blocks on the evenings with the most free time; other days dinner is "eat" only. `"none"` → nothing. |
| Transition time | Between two consecutive events with different `location`, add a `travel` block: `travel_overrides[from→to]` if given, else `transition_minutes`. Same location → 0. |
| Lost time | `lost_time_pct` (default 15%): a `slack` gap after every placed block, and total planned minutes per day ≤ `(1 − pct) × free minutes`. |
| Free time | `free_time_min_per_day` (default 60) reserved as a `free` block, preferably evening. The LLM cannot use it. |

Windows shorter than 25 min are discarded. In **incremental mode** (`pinned` non-empty) this step does not regenerate anything: free windows = waking hours − events − pinned blocks.

### Step 3 — LLM call 1: allocate time to tasks (`allocate.py`)
- **In:** raw task lines (free text, may include "due Fri", "~3h"), today's date, horizon, total free minutes per day.
- **Out:** `TaskPlan[]` — for each task: `deadline`, `priority` (1–3), `estimated_minutes`, `sessions[]` (`minutes` between 25 and 120, `kind: deep|light`), `preferred_time: morning|afternoon|evening|any`.
- Rules in the prompt: session minutes sum to `estimated_minutes`; total must fit in available minutes; if oversubscribed, shrink/drop lowest priority and say why in `notes`.

### Step 4 — LLM call 2: organise and assign time slots (`place.py`)
- **In:** `FreeWindow[]` (with ids) + flat list of sessions (with ids) + deadlines + preferences.
- **Out:** `Placement[] {session_id, start, end}`.
- Rules in the prompt: inside one window, no overlaps, before deadline, ≤ 2 `deep` sessions per day, respect `preferred_time` when possible, spread work rather than cramming the last day.

### Step 5 — Validate / repair / fallback (`validate.py`)
Deterministic checks: every placement inside a free window, no overlaps, duration == session minutes, before deadline, all sessions placed or explicitly dropped.
1. Fail → call 2 once more, with the list of violations appended.
2. Fail again → **greedy fallback**: sort sessions by (deadline, priority), first-fit into windows.
3. Return `warnings[]` (dropped sessions, meal window full, oversubscription).

### Step 6 — Export (`ics_export.py`)
`Block[] → .ics` with stable UIDs and one `CATEGORIES` value per block type. `include_fixed=false` (default) exports only generated blocks (tasks, meals, cooking, travel, free time) so importing doesn't duplicate the student's original events; `true` exports everything.

## 6. API contract (frozen at H0:30)

All datetimes: ISO 8601 with offset, e.g. `2026-09-22T14:00:00+02:00`.

### Endpoints

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/api/health` | — | `{ "ok": true }` |
| POST | `/api/parse-ics` | multipart `file` | `{ events: Event[] }` |
| POST | `/api/schedule` | `ScheduleRequest` | `ScheduleResponse` |
| POST | `/api/export-ics` | `{ blocks: Block[], include_fixed: boolean }` | `text/calendar` attachment |

### Types (TypeScript notation; `models.py` is the pydantic mirror)

```ts
type Event = { id: string; title: string; start: string; end: string; location?: string }

type Settings = {
  timezone: string                      // "Europe/Amsterdam"
  horizon_start: string                 // "2026-09-21"
  horizon_days: number                  // 7
  day_start: string                     // "08:00"
  day_end: string                       // "22:30"
  meals: {
    breakfast?: { window: [string, string]; minutes: number }
    lunch:      { window: [string, string]; minutes: number }   // e.g. ["12:00","13:30"], 30
    dinner:     { window: [string, string]; minutes: number }   // e.g. ["18:30","20:00"], 30
  }
  cooking: { mode: "daily" | "batch" | "none"; batch_per_week: number; cook_minutes: number }
  transition_minutes: number            // default 15
  travel_overrides: { from: string; to: string; minutes: number }[]
  lost_time_pct: number                 // 0–40, default 15
  free_time_min_per_day: number         // default 60
}

type TaskInput = { id: string; text: string }   // "Finish DB assignment, due Fri, ~3h"

type Block = {
  id: string
  type: "event" | "task" | "meal" | "cook" | "travel" | "free" | "slack"
  title: string
  start: string
  end: string
  task_id?: string
  location?: string
  locked?: boolean
}

type Session = { id: string; minutes: number; kind: "deep" | "light" }

type TaskPlan = {
  task_id: string
  title: string
  deadline: string | null
  priority: 1 | 2 | 3
  estimated_minutes: number
  sessions: Session[]
  preferred_time: "morning" | "afternoon" | "evening" | "any"
  notes?: string
}

type ScheduleRequest = {
  events: Event[]
  tasks: TaskInput[]        // only the tasks to plan
  settings: Settings
  pinned?: Block[]          // non-empty => incremental mode
}

type ScheduleResponse = {
  blocks: Block[]           // fixed blocks + task blocks (+ pinned, echoed back)
  task_plans: TaskPlan[]
  warnings: string[]
}
```

### Add / remove tasks (how it works)
- **Remove:** frontend deletes that task's blocks locally and instantly (no LLM). Optional "Re-plan" button = full replan.
- **Add:** frontend calls `/api/schedule` with `tasks: [newTask]` and `pinned: <all current blocks>`. The backend only fills the remaining gaps → fast, and nothing the student already saw moves.
- **Re-plan everything:** `tasks: <all>`, `pinned: []`.

## 7. LLM layer (`llm.py`)
- `call_json(system, user, schema)` → call model, strip code fences, `json.loads`, validate with pydantic; on failure retry once with the error message appended. `temperature` 0.2, 60 s timeout.
- Prompts live in `backend/app/prompts/*.md` with `{{placeholders}}`; C owns and iterates on them.
- **Demo safety:** on-disk cache keyed by the hash of the request, plus `DEMO_MODE=1` returning `fixtures/schedule.mock.json`. If the wifi or API dies during the pitch, the demo still runs.
- Latency: two calls ≈ 10–25 s. The UI must show a two-step progress state ("Estimating time…", "Placing tasks…").

## 8. Frontend

Single page, no router.
- **Sidebar:** `.ics` upload (calls `/api/parse-ics`) · settings accordion (locations/transition, meals, cooking frequency, lost time, free time) · task list (add / remove, one line each) · **Plan my week** button.
- **Main:** FullCalendar `timeGridWeek`, colour by block type, legend, warnings banner, **Download .ics** button.
- **Interactions:** click a task block → delete or lock. Drag a block → it becomes `locked` (stretch).
- **State:** `useReducer` holding `events, tasks, settings, blocks, warnings, status`; settings and tasks mirrored to `localStorage`.
- **Mock switch:** `VITE_USE_MOCK=1` makes `api.ts` return `fixtures/schedule.mock.json`.

## 9. Failure modes and fallbacks

| Failure | Handling |
|---|---|
| LLM returns invalid JSON | retry once → greedy fallback |
| LLM overlaps / breaks deadline | validation catches → retry with violations → greedy fallback |
| More work than free time | drop lowest priority sessions, surface in `warnings` |
| Meal window fully busy | warning, no meal block |
| API/network down | `DEMO_MODE` / cache |
| Bad `.ics` | 422 with message, UI toast |

## 10. Testing
- `pytest` for the pure functions: `ics_parse`, `constraints`, `validate`, `ics_export` (run on `fixtures/sample_calendar.ics`).
- Manual E2E checklist in `plan.md`. Round-trip check: exported `.ics` must import cleanly into Google Calendar or Apple Calendar.

## 11. Non-goals
Auth, database, Google/Outlook OAuth sync, multi-user, mobile layout, real travel-time APIs, deployment.

## 12. Cursor rules (paste into `.cursorrules` on both instances)
```
- Read architecture.md before coding. Section 6 (API contract) is frozen: never rename fields or change types silently.
- Only edit files in your own directory (A: backend/, B: frontend/). If you need a change elsewhere, stop and tell the team.
- Prefer the simplest thing that works. No new dependencies without asking.
- Every LLM output is untrusted: validate with pydantic, never index into it blindly.
- Keep functions pure and small; put logic in constraints.py / validate.py, not in route handlers.
```
