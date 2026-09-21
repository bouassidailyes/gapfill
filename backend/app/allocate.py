"""Turn tasks into TaskPlan[] without an LLM: use the student's minutes, then split sessions."""

from __future__ import annotations

import re

from app.models import Session, TaskInput, TaskPlan

MAX_SESSION = 90
MIN_SESSION = 25


def allocate(
    tasks: list[TaskInput],
    today: str,
    horizon_days: int,
    free_minutes_per_day: dict[str, int],
) -> list[TaskPlan]:
    _ = today, horizon_days, free_minutes_per_day
    plans: list[TaskPlan] = []
    for task in tasks:
        minutes = task.estimated_minutes or _minutes_from_text(task.text) or 60
        minutes = max(MIN_SESSION, min(minutes, 8 * 60))
        plans.append(
            TaskPlan(
                task_id=task.id,
                title=_title(task.text),
                deadline=None,
                priority=2,
                estimated_minutes=minutes,
                sessions=_split(task.id, minutes),
                preferred_time="any",
            )
        )
    return plans


def _split(task_id: str, minutes: int) -> list[Session]:
    remaining = minutes
    sessions: list[Session] = []
    index = 1
    while remaining > 0:
        chunk = min(MAX_SESSION, remaining)
        if remaining > MAX_SESSION and remaining - MAX_SESSION < MIN_SESSION:
            chunk = remaining // 2
        kind = "deep" if chunk >= 50 else "light"
        sessions.append(Session(id=f"{task_id}-s{index}", minutes=chunk, kind=kind))
        remaining -= chunk
        index += 1
    return sessions


def _minutes_from_text(text: str) -> int | None:
    hours = re.search(r"~?\s*(\d+(?:\.\d+)?)\s*h(?:ours?)?\b", text, re.I)
    if hours:
        return int(float(hours.group(1)) * 60)
    mins = re.search(r"~?\s*(\d+)\s*m(?:in(?:utes?)?)?\b", text, re.I)
    if mins:
        return int(mins.group(1))
    return None


def _title(text: str) -> str:
    cleaned = re.sub(r",?\s*due\b.*", "", text, flags=re.I)
    cleaned = re.sub(r",?\s*~?\s*\d+(?:\.\d+)?\s*(?:h(?:ours?)?|m(?:in(?:utes?)?)?)\b", "", cleaned, flags=re.I)
    return cleaned.strip(" ,") or text.strip()
