"""LLM call 2: FreeWindow[] + sessions → Placement[]. (Phase 3)"""

from __future__ import annotations

from app.models import FreeWindow, Placement, TaskPlan


def place(windows: list[FreeWindow], task_plans: list[TaskPlan]) -> list[Placement]:
    raise NotImplementedError("place.py is implemented in phase 3")
