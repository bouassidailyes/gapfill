"""Place sessions into free windows. First-fit; never overlap classes or meals."""

from __future__ import annotations

from datetime import datetime, timedelta

from app.models import Block, FreeWindow, Placement, TaskPlan

MIN_WINDOW = timedelta(minutes=25)


def greedy_place(
    windows: list[FreeWindow],
    task_plans: list[TaskPlan],
) -> tuple[list[Block], list[str]]:
    slots = [_Slot(w) for w in windows]
    slots.sort(key=lambda s: s.start)
    blocks: list[Block] = []
    warnings: list[str] = []

    for plan in task_plans:
        for session in plan.sessions:
            placed = _first_fit(slots, session.minutes)
            if placed is None:
                warnings.append(
                    f"Could not fit '{plan.title}' ({session.minutes} min) around classes and commitments."
                )
                continue
            start, end = placed
            blocks.append(
                Block(
                    id=session.id,
                    type="task",
                    title=plan.title,
                    start=start.isoformat(),
                    end=end.isoformat(),
                    task_id=plan.task_id,
                )
            )
    return blocks, warnings


def validate_and_repair(
    placements: list[Placement],
    windows: list[FreeWindow],
    task_plans: list[TaskPlan],
) -> tuple[list[Block], list[str]]:
    _ = placements
    return greedy_place(windows, task_plans)


class _Slot:
    def __init__(self, window: FreeWindow) -> None:
        self.start = datetime.fromisoformat(window.start)
        self.end = datetime.fromisoformat(window.end)


def _first_fit(slots: list[_Slot], minutes: int) -> tuple[datetime, datetime] | None:
    need = timedelta(minutes=minutes)
    for slot in slots:
        if slot.end - slot.start >= need:
            start = slot.start
            end = start + need
            slot.start = end
            return start, end
    return None
