# AI Student Scheduler — Dev Process Plan

From the first scaffold commit to the last commit: **6 phases**, each ending on a **gate** (exit criteria), a **merge to `main`** and a **git tag**. Design lives in `architecture.md`; who does what by the hour lives in `tasks.md`.

**MVP = done when all five hold:**
1. Upload a real timetable (`.csv` from UM, or `.ics`) and paste 6–8 tasks in plain language.
2. **Plan my week** → week calendar with tasks, meals, cooking, travel and free time; no overlaps, deadlines respected.
3. Add a task → it fills existing gaps without moving anything. Remove a task → it disappears.
4. **Download .ics** → imports cleanly into Google/Apple Calendar.
5. The whole thing survives a bad LLM answer and a dead network (validation + fallback + `DEMO_MODE`).

## Overview

| # | Phase | Time | Gate | Tag |
|---|---|---|---|---|
| 1 | Scaffold & contract | H0:00–1:00 | Mock week renders, backend up, contract frozen | `p1-scaffold` |
| 2 | Engine & inputs (on mocks) | H1:00–2:00 | Constraints + ICS parsing tested, sidebar works, prompts v1 valid | `p2-engine` |
| 3 | Integration: first end-to-end | H2:00–2:30 | Sample inputs → real calendar, even if ugly | `p3-e2e` |
| 4 | Reliability & features | H2:30–4:00 | All Must items done, then **feature freeze** | `p4-features` |
| 5 | Freeze & harden | H4:00–4:30 | QA checklist green, one-command startup | `p5-freeze` |
| 6 | Ship | H4:30–5:00 | Fresh clone runs, submitted, pitch rehearsed | `v1.0-submission` |

Assumes submission at H5:00. Confirm the real deadline at kickoff and shift Phases 5–6 earlier if needed; never shorten Phase 3.

## Rules for every phase

- **Branches:** `be` (A), `fe` (B), `content` (C). Ownership by directory: `backend/` A · `frontend/` B · `backend/app/prompts/`, `fixtures/`, `docs/` C. C pairs at A's or B's screen for prompt wording, UX calls and diff review.
- **Commits:** small and frequent, `type(scope): message`, e.g. `feat(be): meal blocks`, `fix(fe): task delete`, `test(be): validate overlaps`, `docs: demo script`. Pull with `--rebase` before every push.
- **Contract changes:** `models.py` (A) and `types.ts` (B) must match. Any change to `architecture.md` §6 → post in the group chat **before** editing, then update both files in the same hour.
- **Smoke test** (run before every merge to `main`):
  ```
  cd backend && pytest -q
  uvicorn app.main:app --port 8000 &   curl -s localhost:8000/api/health
  cd frontend && npm run build
  ```
  From Phase 3 on, add: `curl -s -X POST localhost:8000/api/schedule -H 'Content-Type: application/json' -d @fixtures/schedule.request.json`.
- **Merge protocol:** smoke test green → rebase on `main` → merge → tag at the gate → announce in chat. The person merging last resolves conflicts.
- **From Phase 3, `main` always runs.** Never merge something that fails the smoke test.

---

## Phase 1 — Scaffold & contract (H0:00–1:00)

**Goal:** everyone can run their part, and nobody will ever wait on anyone else's code.

**Entry:** pre-flight done (Python 3.11+, Node 20+, git, Cursor logged in on both machines, API key tested with a one-line `curl`). Check the hackathon rules first: environment setup and test data are usually fine, pre-written app code usually isn't.

**Steps**
1. **Repo (all, 0:00–0:15):** create/clone, `.gitignore` (`node_modules`, `.venv`, `__pycache__`, `.env`, `cache/`), `.env.example` (`ANTHROPIC_API_KEY`, `LLM_MODEL`, `DEMO_MODE`), README stub, branches `be` / `fe` / `content`. Confirm deadline and track.
2. **Cursor setup (A, B):** paste `architecture.md` §12 into `.cursorrules`; add `@architecture.md` as context in the first chat.
3. **Contract freeze (all, by 0:30):** A writes `backend/app/models.py` from §6; B writes `frontend/src/types.ts`. Compare side by side. Freeze.
4. **Backend scaffold (A):** venv, install `fastapi uvicorn pydantic icalendar recurring-ical-events python-dateutil anthropic pytest`, `requirements.txt`, `app/main.py` with CORS and `GET /api/health`.
5. **Frontend scaffold (B):** `npm create vite@latest frontend -- --template react-ts`, add FullCalendar packages, Vite proxy `/api` → `:8000`, `api.ts` with `VITE_USE_MOCK`, week view rendering `schedule.mock.json` with a colour per block type.
6. **Fixtures (C):** `sample_calendar.ics` (anonymised real week: recurring event, all-day event, two locations), `sample_tasks.txt` (8 tasks: deadlines, vague, none), `settings.json`. **By 0:45:** hand-written `schedule.mock.json` and `allocation.mock.json` (~25 blocks over 7 days).
7. **Contract check (A, 0:45):** validate the mocks against pydantic: `python -c "from app.models import ScheduleResponse; ScheduleResponse.model_validate_json(open('../fixtures/schedule.mock.json').read())"`. Fix whichever side is wrong.
8. **Timetable parse (A, last 15 min):** `csv_parse.py` + `POST /api/parse-csv` (primary: the UM export) and `ics_parse.py` + `POST /api/parse-ics`, both on the sample files.

**Gate**
- [ ] `curl localhost:8000/api/health` returns `{"ok": true}`
- [ ] `npm run dev` shows the mock week in the browser
- [ ] Mocks validate against `models.py`
- [ ] All three branches merged to `main`; a fresh `git pull` runs on every machine

**Tag:** `p1-scaffold`

**Watch out for:** spending 40 minutes on styling or tooling. Anything that isn't in the gate waits.

---

## Phase 2 — Engine & inputs, on mocks (H1:00–2:00)

**Goal:** the deterministic half of the system works and is tested, and the inputs can be entered, without any LLM.

**Steps**
1. **Constraints engine (A):** build `constraints.py` in this order, one commit each, with a `pytest` case per rule: waking hours → meals → cooking (`daily` / `batch` / `none`) → travel blocks → free-time block → slack → `FreeWindow[]`.
2. **Window dump (A, by 1:30):** a small script writing `free_windows.json` for the sample week, so C can test prompts on real data.
3. **Sidebar (B):** `.ics` upload (calls `/api/parse-ics`, shows events on the calendar), settings form (locations/transition, meals, cooking frequency, lost time %, free time), task list with add/remove, **Plan my week** button with loading and error states.
4. **Prompts v1 (C):** `allocate.md` and `place.md`, each with role, inputs (`{{placeholders}}`), hard rules, the exact output JSON schema and one worked example. JSON only, no fences, no prose. Test by hand on the fixtures; log every failure in `docs/bugs.md` as *input → what the model did → fix (prompt or code)*.
5. **Smoke-test assets (C):** `README.md` (how to run) and `fixtures/schedule.request.json` (events + tasks + settings) for `curl` tests.

**Gate (Checkpoint 1, H2:00)**
- [ ] `pytest -q` green on the sample calendar
- [ ] `/api/parse-csv` and `/api/parse-ics` return correct events, including the all-day and recurring ones
- [ ] Free windows look right by eye: none overlaps an event, none shorter than 25 min, meals present, one free-time block per day
- [ ] Sidebar uploads a file and renders the events; settings and tasks are captured in state
- [ ] Both prompts return valid JSON on the normal scenario

**Tag:** `p2-engine`

**Watch out for:** the constraints engine growing. Stick to the rules in `architecture.md` §5 step 2; anything fancier is a "Could".

---

## Phase 3 — Integration: first end-to-end (H2:00–2:30)

**Goal:** one real path from input to calendar. Ugly is fine; wrong data flow is not.

**Steps**
1. **LLM layer (A):** `llm.py` (`call_json`: parse, pydantic-validate, retry once), `allocate.py`, `place.py`, wire `POST /api/schedule` with C's prompts. Prompts are loaded from `backend/app/prompts/*.md`.
2. **Switch off mocks (B):** `VITE_USE_MOCK=0`, connect to `/api/schedule`, show the two-step progress ("Estimating time…", "Placing tasks…") and a warnings banner.
3. **Sit together (A + B, 30 min):** integrate in one window. If the two sides disagree, fix the contract first (`architecture.md` §6 → both files), then the code.
4. **First QA (C):** run the QA checklist (Phase 5) the moment a plan appears. File bugs as P0/P1, each tagged "prompt" or "code". Bug list in A's and B's hands by 2:35.

**Gate (Checkpoint 2, H2:30)**
- [ ] Sample calendar + sample tasks → **Plan my week** → real blocks on the calendar
- [ ] The `curl` smoke test on `/api/schedule` returns a valid `ScheduleResponse`
- [ ] Failures known and listed (invalid outputs are expected at this stage: validation is Phase 4)

**Tag:** `p3-e2e`. From here on, `main` always runs.

**Watch out for:** latency (10–25 s per plan). Do not optimise now; the progress UI and the cache in Phase 4 are enough.

---

## Phase 4 — Reliability & features (H2:30–4:00)

**Goal:** turn the demo path into something that cannot embarrass you, then finish the Must list. **Reliability first, features second.**

**4a — Reliability (H2:30–3:15)**
1. **`validate.py` (A):** checks (inside a free window, no overlaps, duration matches, before deadline, every session placed or dropped) → retry `place` once with the violations → **greedy fallback** (sort by deadline then priority, first-fit). Return `warnings[]`.
2. **Proof test (A):** feed deliberately broken LLM output (overlaps, missed deadline, bad JSON) and assert a valid calendar comes out. Merge only when green.
3. **Prompts v2 (C):** fix the "prompt" bugs; move every "code" bug to A as a validation rule instead of another prompt patch. Test the **overloaded** and **no-deadline** scenarios.
4. **Resilience (A):** response cache keyed by request hash + `DEMO_MODE=1` returning `fixtures/schedule.mock.json`.

**4b — Features (H3:00–4:00)**
5. **Export (A):** `ics_export.py` (`include_fixed` toggle, stable UIDs) + `POST /api/export-ics`, with tests. **B:** Download button, task-block click → delete / lock.
6. **Incremental add (A + B):** `pinned` blocks → free windows without regenerating meals/travel. **B:** add-task calls `/api/schedule` with `tasks:[new]` and `pinned: current blocks`; remove is local and instant.
7. **Polish (B):** legend, empty states, `localStorage` persistence for settings and tasks.
8. **Verify in the real world (C):** import the exported `.ics` into Google or Apple Calendar and check the times; regression-run all three scenarios; draft the demo script and slides.

**Gate (H4:00, all Must items)**
- [ ] Broken-LLM test passes: a valid calendar always comes out
- [ ] Overloaded scenario shows a warning and drops low-priority work; the app doesn't crash
- [ ] Add a task → existing blocks don't move. Remove a task → blocks disappear
- [ ] Exported `.ics` opens in a real calendar app with correct times
- [ ] `DEMO_MODE=1` works with the network off

**Tag:** `p4-features`. **Then announce FEATURE FREEZE in the chat.**

**If it slips, cut in this order:** drag-to-lock → edit-minutes step → "why this slot" tooltips → batch cooking (keep `daily` and `none`) → per-pair travel overrides (keep the single default) → incremental mode (add = full replan with a "things may move" warning). **Never cut:** validation + fallback, `.ics` export, `DEMO_MODE`.

---

## Phase 5 — Freeze & harden (H4:00–4:30)

**Goal:** no new features. Make what exists reliable and presentable.

**Rules during the freeze:** P0 bugs only, no refactors, no new dependencies, every fix comes from a bug in `docs/bugs.md` with a repro, and someone other than the author reruns the smoke test after each fix.

**Steps**
1. **Fix P0 bugs (A, B).** Small commits directly reviewed by C at the screen.
2. **QA pass (C):** run the full checklist below; anything unfixable goes into the README under "Known issues".
3. **One-command startup (A):** `make dev` or `run.sh` starts backend + frontend; README updated to match.
4. **Warm the cache (A):** run the exact demo scenario twice so the cache and `DEMO_MODE` fixtures are current.
5. **Backup video (B):** screen-record the full demo path.
6. **Slides + first dry run (C):** 3–5 slides (problem, solution, "LLM proposes, code guarantees", demo, next steps); one timed run-through.

**QA checklist**
- [ ] Upload sample `.csv`: events correct (times, all-day row, locations)
- [ ] Upload sample `.ics`: events correct (recurring, all-day, two locations)
- [ ] Plan with 8 tasks: no overlaps, everything inside waking hours
- [ ] Every task with a deadline is placed before it
- [ ] Meals every day; cooking follows the chosen frequency
- [ ] Travel blocks only between events at different locations
- [ ] Lost time and free time visibly respected (gaps + a free block per day)
- [ ] Overloaded week: warning shown, lowest-priority work dropped, no crash
- [ ] Add a task: placed in existing gaps, nothing else moves
- [ ] Remove a task: its blocks disappear
- [ ] Download `.ics`: imports into Google or Apple Calendar with correct times
- [ ] Invalid `.csv` / `.ics`: readable error, no crash
- [ ] `DEMO_MODE=1` works with no network

**Gate**
- [ ] QA checklist all ticked, or each failure documented as a known issue
- [ ] A fresh clone starts with one command
- [ ] Backup video saved; slides exist; one timed dry run done

**Tag:** `p5-freeze`

**Watch out for:** "one small improvement". Every unplanned change after H4:00 is a demo risk; write it in `docs/next-steps.md` instead (it makes the closing slide better).

---

## Phase 6 — Ship (H4:30–5:00)

**Goal:** a verified last commit, a submitted project, a rehearsed pitch.

**Steps**
1. **Final merge (4:30–4:40):** merge `be`, `fe`, `content` into `main`. Smoke test green.
2. **Fresh-clone verification (A or B, 5 min):** `git clone <repo> /tmp/final && cd /tmp/final`, follow the README exactly, run the demo scenario once with the network on and once with `DEMO_MODE=1`. If anything needs a step that isn't in the README, fix the README.
3. **The last commit:** `git tag v1.0-submission && git push --tags`. After this tag only README/docs edits, and only if the platform allows it.
4. **Submit** whatever the platform needs: repo link, tag, backup video, slides.
5. **Rehearse (4:40–5:00):** two full runs, C leading. Split: **C** problem + close, **B** live demo, **A** "how it works" + Q&A. A and B stay ready to fix a P0 only.

**If a P0 shows up after the tag:** fix on `main`, rerun the fresh-clone check, tag `v1.0.1`, resubmit. Otherwise leave it alone.

**Demo script (3 min)**
1. **Problem (20 s):** students juggle a fixed timetable, assignments, cooking, commuting and a life. Calendars store events; nobody plans the *rest*.
2. **Input (30 s):** upload the calendar, paste tasks in plain language ("DB assignment due Friday, ~3h, gym twice, prep group presentation").
3. **Settings (20 s):** locations, cook 3× per week, 15% lost time, 1 h free time per day.
4. **Plan (40 s):** click; show the two-step progress, then the week.
5. **Explain (30 s):** travel blocks, cooking, free time, a deadline respected, the overload warning.
6. **Live edit (20 s):** add a task, watch it fill a gap; remove one.
7. **Export (10 s):** download the `.ics`, show it open in a calendar app.
8. **Close (10 s):** next steps (OAuth calendar sync, real travel times, learning from what the student actually completes).

**Pitch angle:** best fit is the **Maastricht Challenge** (student life) track. Lead with the student problem, not the tech. "LLM proposes, code guarantees" is the talking point: it's why the schedule can be trusted.

**Gate**
- [ ] `v1.0-submission` tag pushed and verified on a fresh clone
- [ ] Submitted
- [ ] Two rehearsals done, everyone knows their part

**Tag:** `v1.0-submission`
