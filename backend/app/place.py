"""LLM call 2: FreeWindow[] + sessions → Placement[]."""

from __future__ import annotations

import json

from app.llm import call_json, fill_prompt
from app.models import FreeWindow, PlaceOutput, Placement, TaskPlan

SYSTEM = "You place work sessions into free windows. Return JSON only. No markdown."


def place(
    windows: list[FreeWindow],
    task_plans: list[TaskPlan],
    violations: list[str] | None = None,
) -> list[Placement]:
    sessions = [
        {
            "id": session.id,
            "task_id": plan.task_id,
            "title": plan.title,
            "minutes": session.minutes,
            "kind": session.kind,
            "deadline": plan.deadline,
            "preferred_time": plan.preferred_time,
            "priority": plan.priority,
        }
        for plan in task_plans
        for session in plan.sessions
    ]
    user = fill_prompt(
        "place",
        windows=json.dumps([w.model_dump() for w in windows]),
        sessions=json.dumps(sessions),
        task_plans=json.dumps([p.model_dump() for p in task_plans]),
    )
    if violations:
        user += "\n\nThe previous placements broke these rules:\n- " + "\n- ".join(violations)
        user += "\nFix every violation. Stay inside the given windows."
    return call_json(SYSTEM, user, PlaceOutput).placements
