"""Window / overlap / deadline checks, one retry, then greedy fallback. (Phase 4)"""

from __future__ import annotations

from app.models import Block, FreeWindow, Placement, TaskPlan


def validate_and_repair(
    placements: list[Placement],
    windows: list[FreeWindow],
    task_plans: list[TaskPlan],
) -> tuple[list[Block], list[str]]:
    raise NotImplementedError("validate.py is implemented in phase 4")
