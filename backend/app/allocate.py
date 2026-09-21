"""LLM call 1: free-text tasks → TaskPlan[]. (Phase 3)"""

from __future__ import annotations

from app.models import TaskInput, TaskPlan


def allocate(tasks: list[TaskInput], today: str, horizon_days: int, free_minutes_per_day: dict[str, int]) -> list[TaskPlan]:
    raise NotImplementedError("allocate.py is implemented in phase 3")
