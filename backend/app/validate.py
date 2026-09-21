"""Window / overlap / deadline checks, then greedy fallback."""

from __future__ import annotations

from datetime import datetime, timedelta

from app.models import Block, FreeWindow, Placement, Session, TaskPlan

MIN_WINDOW = timedelta(minutes=25)


def check_placements(
    placements: list[Placement],
    windows: list[FreeWindow],
    task_plans: list[TaskPlan],
) -> list[str]:
    sessions = _session_index(task_plans)
    bounds = [(_dt(w.start), _dt(w.end)) for w in windows]
    violations: list[str] = []
    used: list[tuple[datetime, datetime, str]] = []
    seen: set[str] = set()
    deep_by_day: dict[str, int] = {}

    for placement in placements:
        session = sessions.get(placement.session_id)
        if session is None:
            violations.append(f"Unknown session_id {placement.session_id}.")
            continue
        if placement.session_id in seen:
            violations.append(f"Session {placement.session_id} was placed twice.")
            continue
        seen.add(placement.session_id)
        try:
            start, end = _dt(placement.start), _dt(placement.end)
        except ValueError:
            violations.append(f"{placement.session_id} has an unreadable time.")
            continue
        plan, spec = session
        duration = (end - start).total_seconds() / 60
        if abs(duration - spec.minutes) > 1:
            violations.append(
                f"{placement.session_id} lasts {duration:.0f} min, expected {spec.minutes}."
            )
        if not any(lo <= start and end <= hi for lo, hi in bounds):
            violations.append(f"{placement.session_id} is not inside a free window.")
        for other_start, other_end, other_id in used:
            if start < other_end and other_start < end:
                violations.append(f"{placement.session_id} overlaps {other_id}.")
        used.append((start, end, placement.session_id))
        if plan.deadline:
            try:
                if end > _dt(plan.deadline):
                    violations.append(f"{placement.session_id} is after the deadline.")
            except ValueError:
                pass
        if spec.kind == "deep":
            day = start.date().isoformat()
            deep_by_day[day] = deep_by_day.get(day, 0) + 1
            if deep_by_day[day] > 2:
                violations.append(f"More than two deep sessions on {day}.")
    return violations


def placements_to_blocks(
    placements: list[Placement],
    task_plans: list[TaskPlan],
) -> tuple[list[Block], list[str]]:
    sessions = _session_index(task_plans)
    blocks: list[Block] = []
    placed: set[str] = set()
    for placement in placements:
        session = sessions.get(placement.session_id)
        if session is None:
            continue
        plan, spec = session
        placed.add(spec.id)
        blocks.append(
            Block(
                id=spec.id,
                type="task",
                title=plan.title,
                start=placement.start,
                end=placement.end,
                task_id=plan.task_id,
            )
        )
    warnings = [
        f"Dropped '{plan.title}' ({spec.minutes} min): no valid slot."
        for plan in task_plans
        for spec in plan.sessions
        if spec.id not in placed
    ]
    return blocks, warnings


def greedy_place(
    windows: list[FreeWindow],
    task_plans: list[TaskPlan],
) -> tuple[list[Block], list[str]]:
    ordered = sorted(
        task_plans,
        key=lambda p: (p.deadline is None, p.deadline or "", p.priority, -p.estimated_minutes),
    )
    slots = [_Slot(w) for w in windows]
    slots.sort(key=lambda s: s.start)
    blocks: list[Block] = []
    warnings: list[str] = []

    for plan in ordered:
        for spec in plan.sessions:
            placed = _first_fit(slots, spec.minutes, plan.deadline)
            if placed is None:
                warnings.append(
                    f"Could not fit '{plan.title}' ({spec.minutes} min) around classes and commitments."
                )
                continue
            start, end = placed
            blocks.append(
                Block(
                    id=spec.id,
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
    if check_placements(placements, windows, task_plans):
        blocks, warnings = greedy_place(windows, task_plans)
        warnings = ["Used the backup placer after the model broke a rule."] + warnings
        return blocks, warnings
    return placements_to_blocks(placements, task_plans)


class _Slot:
    def __init__(self, window: FreeWindow) -> None:
        self.start = datetime.fromisoformat(window.start)
        self.end = datetime.fromisoformat(window.end)


def _first_fit(
    slots: list[_Slot], minutes: int, deadline: str | None
) -> tuple[datetime, datetime] | None:
    need = timedelta(minutes=minutes)
    limit = _dt(deadline) if deadline else None
    for slot in slots:
        if slot.end - slot.start < need:
            continue
        start = slot.start
        end = start + need
        if limit is not None and end > limit:
            continue
        slot.start = end
        return start, end
    return None


def _session_index(task_plans: list[TaskPlan]) -> dict[str, tuple[TaskPlan, Session]]:
    index: dict[str, tuple[TaskPlan, Session]] = {}
    for plan in task_plans:
        for spec in plan.sessions:
            index[spec.id] = (plan, spec)
    return index


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)
