# Task Repartition — by hour, by person

| Slot | Role | Tooling |
|---|---|---|
| **A** | Backend: parsing, constraints, LLM calls, validation, export | Cursor #1 |
| **B** | Frontend: calendar UI, forms, add/remove, download | Cursor #2 |
| **C** | Content & quality: fixtures, mocks, prompts, QA, docs, pitch | No Cursor (plain editor; pairs with A/B) |

Assign names to slots at kickoff. Times are relative to the hackathon start (H0:00). Confirm the real submission time and shift the tail of the schedule if it's earlier than H5:00.

---

## Hour 1 — H0:00 to H1:00 · Foundations

| | Tasks | Done when |
|---|---|---|
| **All** (0:00–0:30) | Read `architecture.md`. Freeze §6 (contract). Create repo, branches `be`/`fe`/`content`, `.cursorrules` on both Cursor instances. Confirm submission deadline and track. | Everyone can run their part locally |
| **A** | Repo skeleton, FastAPI `/api/health`, `models.py` from §6 (freeze by 0:30). Then `csv_parse.py` (UM timetable export → `Event[]`, `POST /api/parse-csv`) and `ics_parse.py` (recurring, all-day, timezone → `Event[]`, `POST /api/parse-ics`). | Sample `.csv` and `.ics` return correct events |
| **B** | Vite + React + TS scaffold, `types.ts` mirroring §6, `api.ts` with `VITE_USE_MOCK`. FullCalendar `timeGridWeek` rendering `schedule.mock.json`, colour per block type. | Mock week renders in the browser |
| **C** | `fixtures/sample_calendar.ics` (real anonymised week, recurring + all-day + two locations), `sample_tasks.txt` (8 tasks, mix of deadlines/no deadlines/vague), `settings.json`. **By 0:45:** hand-write `schedule.mock.json` and `allocation.mock.json` valid against the schema (realistic: ~25 blocks over 7 days). Draft `allocate.md` v0. | Mocks pushed at 0:45: B is unblocked |

## Hour 2 — H1:00 to H2:00 · Parallel build

| | Tasks | Done when |
|---|---|---|
| **A** | `constraints.py`: sleep/waking hours, meals, cooking (daily/batch), travel blocks, free-time block, slack → `FixedBlock[]` + `FreeWindow[]`. `pytest` on the sample calendar. Script that dumps `free_windows.json` for C by 1:30. | Free windows on the sample week look sane by eye |
| **B** | Sidebar: timetable upload (`.csv` → `/api/parse-csv`, `.ics` → `/api/parse-ics`), settings form (locations/transition, meals, cooking frequency, lost time %, free time), task list with add/remove, **Plan my week** button, loading + error states. | Whole input side works against mock |
| **C** | Prompts v1: finish `allocate.md`, write `place.md`. Test both by hand on the fixtures (use `free_windows.json` from A once it lands). Log failures in `docs/bugs.md`. Write `README.md` (how to run) and `fixtures/schedule.request.json` (events + tasks + settings, for curl smoke tests). Start the QA checklist in `plan.md` (Phase 5 QA checklist). | Both prompts return valid JSON on the normal scenario |

**Checkpoint 1 (H2:00):** `/api/parse-csv`, `/api/parse-ics` and `constraints.py` work on the sample timetable.

## Hour 3 — H2:00 to H3:00 · Integration and reliability

| | Tasks | Done when |
|---|---|---|
| **A** (2:00–2:30) | `llm.py` (`call_json` with retry), `allocate.py`, `place.py`, wire `POST /api/schedule` using C's prompts. | Real end-to-end plan returned |
| **B** (2:00–2:30) | Switch mock off, connect to real `/api/schedule`. Two-step progress state, warnings banner. | Sidebar → Plan → real calendar |
| **C** (2:00–2:30) | Run the full QA checklist the moment the pipeline works; file bugs as P0/P1 in `docs/bugs.md`, tagging each "prompt" or "code". | Bug list in A's and B's hands by 2:35 |
| **A** (2:30–3:00) | `validate.py`: overlap / window / deadline checks, retry with violations, greedy fallback. | Deliberately broken LLM output still yields a valid calendar |
| **B** (2:30–3:00) | Click a task block → delete / lock. Download `.ics` button wired to `/api/export-ics`. Legend. | Delete works; download triggers |
| **C** (2:30–3:00) | Prompts v2 from the bug list. Test **overloaded** and **no-deadline** scenarios. Hand new failure cases to A as validation rules. | Overloaded scenario yields warnings, not garbage |

**Checkpoint 2 (H2:30):** happy path works end to end, even if ugly.

## Hour 4 — H3:00 to H4:00 · Features and hardening

| | Tasks | Done when |
|---|---|---|
| **A** | `ics_export.py` (+ tests). Incremental mode: `pinned` blocks → free windows without regenerating meals/travel. Response cache + `DEMO_MODE`. | Adding a task doesn't move existing blocks |
| **B** | Add-task flow using `pinned = current blocks`, remove-task instant, `localStorage` persistence, empty states, visual polish (spacing, colours, typography). *Could:* drag-to-lock. | Add and remove feel instant and safe |
| **C** | Import the exported `.ics` into Google/Apple Calendar and verify times. Regression run on all 3 scenarios. Write `docs/demo-script.md` from `plan.md` (Phase 6 demo script). Start 3–5 slides (problem, solution, architecture "LLM proposes, code guarantees", demo, next steps). | Export verified in a real calendar app; slides drafted |

**H4:00 — FEATURE FREEZE.** From here: P0 bugs, polish, demo, pitch. No new features.

## Hour 5 — H4:00 to H5:00 · Freeze, rehearse, ship

| | Tasks | Done when |
|---|---|---|
| **A** (4:00–4:30) | Fix P0 bugs. Make startup a one-liner (`make dev` or `run.sh`). Final README check. Pre-run the demo scenario so the cache is warm. | Fresh clone runs with one command |
| **B** (4:00–4:30) | Fix P0 UI bugs. Final polish pass. Record a backup screen capture of the full demo. | Backup video saved |
| **C** (4:00–4:30) | Final QA pass (Phase 5 QA checklist). Finish slides. Demo dry run #1, timed. | Demo fits in 3 minutes |
| **All** (4:30–5:00) | 4:30–4:40 final merge to `main`, tag, submit (whatever the platform needs). 4:40–5:00 two full pitch rehearsals, C leading, A and B on standby for a P0 only. Split the pitch: C problem + close, B live demo, A "how it works" + Q&A. | Submitted, rehearsed, everyone knows their lines |

---

## Handoffs (who is waiting on whom)

| From | To | What | Needed by |
|---|---|---|---|
| A | B | Frozen `models.py` (contract) | 0:30 |
| C | B | `schedule.mock.json` | 0:45 |
| C | A | `sample_calendar.ics` | 0:45 |
| A | C | `free_windows.json` (for prompt testing) | 1:30 |
| C | A | `allocate.md` + `place.md` v1 | 2:00 |
| A | B | Working `/api/schedule` | 2:00–2:30 |
| C | A / B | Prioritised bug list | 2:35, then continuously |
| A | B | `/api/export-ics` | 3:00 |

## Optional handoffs if C can code by hand

Only give C code that is small, pure, and fully specified, so nobody depends on it late:

- `ics_export.py` — `blocks_to_ics(blocks: list[Block], include_fixed: bool) -> bytes` using `icalendar` (about 30 lines). Frees A about 15 minutes in H4. **Fallback:** if it isn't done by 3:00, A generates it with Cursor.
- Greedy fallback inside `validate.py` — sort sessions by (deadline, priority), first-fit into free windows. Pure algorithm, easy to hand-write. **Fallback:** same, A generates it.
- `pytest` cases from the QA scenarios.

If C can't code, keep C on content, QA and pitch: the split above is designed so that nothing on the critical path depends on C writing code.

## If you fall behind

Cut in this order: drag-to-lock → edit-minutes step → "why this slot" tooltips → batch cooking (keep `daily` and `none`) → per-pair travel overrides (keep the single default) → incremental mode (add task = full replan with a warning that things may move). Never cut: validation + fallback, `.ics` export, the demo script.
