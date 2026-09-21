"""LLM call 1: free-text tasks → TaskPlan[]. Falls back to a deterministic split."""

from __future__ import annotations

import json
import re

from typing import Literal

from app.llm import LlmError, call_json, fill_prompt, llm_enabled
from app.models import AllocationOutput, Session, TaskInput, TaskPlan

MAX_SESSION = 90
MIN_SESSION = 25
SYSTEM = "You estimate study time. Return JSON only. No markdown."


def allocate(
    tasks: list[TaskInput],
    today: str,
    horizon_days: int,
    free_minutes_per_day: dict[str, int],
) -> tuple[list[TaskPlan], list[str]]:
    if not tasks:
        return [], []
    if llm_enabled():
        try:
            return _allocate_llm(tasks, today, horizon_days, free_minutes_per_day), []
        except LlmError as exc:
            return allocate_fallback(tasks), [
                f"The model failed to estimate times ({exc}); used backup estimates."
            ]
    return allocate_fallback(tasks), []


def allocate_fallback(tasks: list[TaskInput]) -> list[TaskPlan]:
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


def _allocate_llm(
    tasks: list[TaskInput],
    today: str,
    horizon_days: int,
    free_minutes_per_day: dict[str, int],
) -> list[TaskPlan]:
    user = fill_prompt(
        "allocate",
        today=today,
        horizon_days=str(horizon_days),
        free_minutes_per_day=json.dumps(free_minutes_per_day),
        tasks=json.dumps([t.model_dump() for t in tasks]),
    )
    output = call_json(SYSTEM, user, AllocationOutput)
    by_id = {t.id: t for t in tasks}
    plans = [p for p in output.task_plans if p.task_id in by_id and p.sessions]
    if not plans:
        raise LlmError("Allocation contained no usable task plans.")
    for plan in plans:
        source = by_id[plan.task_id]
        if source.estimated_minutes and abs(plan.estimated_minutes - source.estimated_minutes) > 15:
            plan.estimated_minutes = source.estimated_minutes
            plan.sessions = _split(plan.task_id, source.estimated_minutes)
    return plans


def _split(task_id: str, minutes: int) -> list[Session]:
    remaining = minutes
    sessions: list[Session] = []
    index = 1
    while remaining > 0:
        chunk = min(MAX_SESSION, remaining)
        if remaining > MAX_SESSION and remaining - MAX_SESSION < MIN_SESSION:
            chunk = remaining // 2
        kind: Literal["deep", "light"] = "deep" if chunk >= 50 else "light"
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
    cleaned = re.sub(
        r",?\s*~?\s*\d+(?:\.\d+)?\s*(?:h(?:ours?)?|m(?:in(?:utes?)?)?)\b",
        "",
        cleaned,
        flags=re.I,
    )
    return cleaned.strip(" ,") or text.strip()
