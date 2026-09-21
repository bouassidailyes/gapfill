"""Build a week: fixed classes/commitments, elastic meals, then tasks in leftover gaps."""

from __future__ import annotations

from datetime import datetime

from app.allocate import allocate
from app.constraints import build_constraints, constraint_warnings
from app.models import ScheduleRequest, ScheduleResponse
from app.validate import greedy_place


def build_plan(req: ScheduleRequest) -> ScheduleResponse:
    occupied, windows = build_constraints(req.events, req.settings, req.pinned)
    warnings = constraint_warnings(occupied, req.settings)

    free_per_day: dict[str, int] = {}
    for window in windows:
        day = datetime.fromisoformat(window.start).date().isoformat()
        minutes = int(
            (datetime.fromisoformat(window.end) - datetime.fromisoformat(window.start)).total_seconds()
            / 60
        )
        free_per_day[day] = free_per_day.get(day, 0) + minutes

    task_plans = allocate(
        req.tasks,
        req.settings.horizon_start,
        req.settings.horizon_days,
        free_per_day,
    )
    task_blocks, place_warnings = greedy_place(windows, task_plans)
    warnings.extend(place_warnings)

    blocks = occupied + task_blocks
    blocks.sort(key=lambda b: b.start)
    return ScheduleResponse(blocks=blocks, task_plans=task_plans, warnings=warnings)
