"""LLM proposes task times; code keeps classes, meals and sleep fixed."""

from __future__ import annotations

from datetime import datetime

from app.allocate import allocate
from app.constraints import build_constraints, constraint_warnings
from app.llm import LlmError, llm_enabled
from app.models import ScheduleRequest, ScheduleResponse
from app.place import place
from app.validate import check_placements, greedy_place, placements_to_blocks, validate_and_repair


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

    task_blocks, place_warnings = _place_tasks(windows, task_plans)
    warnings.extend(place_warnings)

    blocks = occupied + task_blocks
    blocks.sort(key=lambda b: b.start)
    return ScheduleResponse(blocks=blocks, task_plans=task_plans, warnings=warnings)


def _place_tasks(windows, task_plans):
    if not task_plans:
        return [], []
    if not llm_enabled():
        return greedy_place(windows, task_plans)
    try:
        placements = place(windows, task_plans)
        violations = check_placements(placements, windows, task_plans)
        if violations:
            placements = place(windows, task_plans, violations)
        return validate_and_repair(placements, windows, task_plans)
    except LlmError:
        blocks, warnings = greedy_place(windows, task_plans)
        return blocks, ["The model failed; used the backup placer."] + warnings
