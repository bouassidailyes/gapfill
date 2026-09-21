from __future__ import annotations

from datetime import datetime

from app.models import Event, ScheduleRequest, Settings, TaskInput
from app.planner import build_plan

SETTINGS = Settings.model_validate(
    {
        "timezone": "Europe/Amsterdam",
        "horizon_start": "2026-09-21",
        "horizon_days": 7,
        "day_start": "08:00",
        "day_end": "22:30",
        "meals": {
            "lunch": {"window": ["12:00", "13:30"], "minutes": 30},
            "dinner": {"window": ["18:30", "20:00"], "minutes": 30},
        },
        "cooking": {"mode": "none", "batch_per_week": 3, "cook_minutes": 45},
        "transition_minutes": 15,
        "travel_overrides": [],
        "lost_time_pct": 15,
        "free_time_min_per_day": 60,
    }
)


def _event(title: str, start: str, end: str, location: str = "UM Campus") -> Event:
    return Event(id=title, title=title, start=start, end=end, location=location)


def _overlap(a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
    return a_start < b_end and b_start < a_end


def test_classes_never_move_and_meals_slide_around_them() -> None:
    lecture = _event("Databases", "2026-09-21T12:00:00+02:00", "2026-09-21T14:00:00+02:00")
    plan = build_plan(ScheduleRequest(events=[lecture], tasks=[], settings=SETTINGS))
    classes = [b for b in plan.blocks if b.type == "event"]
    assert classes[0].start == lecture.start
    assert classes[0].end == lecture.end
    lunch = next(b for b in plan.blocks if b.type == "meal" and b.title == "Lunch")
    assert not _overlap(lunch.start, lunch.end, lecture.start, lecture.end)
    # 12:00–13:30 is blocked, so lunch moves to a nearby gap (here 11:00).
    assert lunch.end <= lecture.start or lunch.start >= lecture.end


def test_nothing_is_placed_before_wake_or_after_sleep() -> None:
    late = SETTINGS.model_copy(update={"day_start": "10:00", "day_end": "20:00"})
    plan = build_plan(ScheduleRequest(events=[], tasks=[], settings=late))
    for block in plan.blocks:
        start = datetime.fromisoformat(block.start)
        if block.start.endswith("T00:00:00+02:00"):
            continue
        assert start.hour >= 10
        end = datetime.fromisoformat(block.end)
        assert end.hour < 20 or (end.hour == 20 and end.minute == 0)


def test_weekly_commitment_beats_homework() -> None:
    gym = _event("Gym", "2026-09-22T19:00:00+02:00", "2026-09-22T19:45:00+02:00")
    task = TaskInput(id="t1", text="Essay", estimated_minutes=180)
    plan = build_plan(ScheduleRequest(events=[gym], tasks=[task], settings=SETTINGS))
    homework = [b for b in plan.blocks if b.type == "task"]
    assert any(b.title == "Gym" for b in plan.blocks)
    for block in homework:
        assert not _overlap(block.start, block.end, gym.start, gym.end)


def test_task_uses_estimated_minutes() -> None:
    task = TaskInput(id="t1", text="Problem set", estimated_minutes=90)
    plan = build_plan(ScheduleRequest(events=[], tasks=[task], settings=SETTINGS))
    homework = [b for b in plan.blocks if b.task_id == "t1"]
    total = sum(
        int(
            (datetime.fromisoformat(b.end) - datetime.fromisoformat(b.start)).total_seconds() / 60
        )
        for b in homework
    )
    assert total == 90
