"""Settings → FixedBlock[] + FreeWindow[]. Deterministic; no LLM."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.models import Block, Event, FreeWindow, MealSpec, Settings

MIN_WINDOW = timedelta(minutes=25)
LUNCH_FALLBACK = (time(11, 0), time(15, 0))
DINNER_FALLBACK = (time(17, 0), time(21, 0))


def build_constraints(
    events: list[Event],
    settings: Settings,
    pinned: list[Block] | None = None,
) -> tuple[list[Block], list[FreeWindow]]:
    tz = ZoneInfo(settings.timezone)
    horizon = date.fromisoformat(settings.horizon_start)
    day_start = _hhmm(settings.day_start)
    day_end = _hhmm(settings.day_end)

    event_blocks = [_event_block(e) for e in events]
    if pinned:
        occupied = event_blocks + [b for b in pinned if b.type != "event"]
        windows = _windows_from_occupied(occupied, settings, tz, horizon, day_start, day_end)
        return occupied, windows

    occupied: list[Block] = list(event_blocks)

    for offset in range(settings.horizon_days):
        day = horizon + timedelta(days=offset)
        wake = datetime.combine(day, day_start, tzinfo=tz)
        sleep = datetime.combine(day, day_end, tzinfo=tz)
        busy = _busy_on_day(event_blocks, wake, sleep)

        lunch, _lunch_warn = _place_meal("lunch", settings.meals.lunch, day, wake, sleep, busy, tz)
        if lunch:
            occupied.append(lunch)
            busy.append((_dt(lunch.start), _dt(lunch.end)))

        dinner, _dinner_warn = _place_meal("dinner", settings.meals.dinner, day, wake, sleep, busy, tz)
        if dinner:
            occupied.append(dinner)
            busy.append((_dt(dinner.start), _dt(dinner.end)))

        if settings.meals.breakfast:
            breakfast, _ = _place_meal(
                "breakfast", settings.meals.breakfast, day, wake, sleep, busy, tz
            )
            if breakfast:
                occupied.append(breakfast)
                busy.append((_dt(breakfast.start), _dt(breakfast.end)))

        if settings.cooking.mode == "daily" and dinner:
            cook = _place_cook_before(dinner, settings.cooking.cook_minutes, wake, busy, day, tz)
            if cook:
                occupied.append(cook)
                busy.append((_dt(cook.start), _dt(cook.end)))

        if settings.free_time_min_per_day > 0:
            free = _place_free(day, settings.free_time_min_per_day, wake, sleep, busy, tz)
            if free:
                occupied.append(free)
                busy.append((_dt(free.start), _dt(free.end)))

    if settings.cooking.mode == "batch":
        occupied.extend(_place_batch_cooks(occupied, settings, tz, horizon, day_start, day_end))

    windows = _windows_from_occupied(occupied, settings, tz, horizon, day_start, day_end)
    # warnings are attached by the planner; constraints only returns blocks + windows
    return occupied, windows


def constraint_warnings(occupied: list[Block], settings: Settings) -> list[str]:
    """Surface days that ended up without a meal."""
    tz = ZoneInfo(settings.timezone)
    horizon = date.fromisoformat(settings.horizon_start)
    notes: list[str] = []
    for offset in range(settings.horizon_days):
        day = horizon + timedelta(days=offset)
        meals = [
            b
            for b in occupied
            if b.type == "meal" and _dt(b.start).astimezone(tz).date() == day
        ]
        titles = {b.title.lower() for b in meals}
        label = day.strftime("%A")
        if not any("lunch" in t for t in titles):
            notes.append(f"{label}: no gap for lunch around classes.")
        if not any("dinner" in t for t in titles):
            notes.append(f"{label}: no gap for dinner around classes.")
    return notes


def _place_meal(
    name: str,
    spec: MealSpec,
    day: date,
    wake: datetime,
    sleep: datetime,
    busy: list[tuple[datetime, datetime]],
    tz: ZoneInfo,
) -> tuple[Block | None, str | None]:
    preferred = (_hhmm(spec.window[0]), _hhmm(spec.window[1]))
    fallback = LUNCH_FALLBACK if name == "lunch" else DINNER_FALLBACK if name == "dinner" else preferred
    duration = timedelta(minutes=spec.minutes)
    slot = _find_gap(wake, sleep, busy, duration, preferred, tz, day) or _find_gap(
        wake, sleep, busy, duration, fallback, tz, day
    )
    if slot is None:
        slot = _find_gap(wake, sleep, busy, duration, (wake.time(), sleep.time()), tz, day)
    if slot is None:
        return None, f"{day.strftime('%A')}: no gap for {name}."
    start, end = slot
    return (
        Block(
            id=f"meal-{name}-{day.isoformat()}",
            type="meal",
            title=name.capitalize(),
            start=start.isoformat(),
            end=end.isoformat(),
        ),
        None,
    )


def _place_cook_before(
    dinner: Block,
    minutes: int,
    wake: datetime,
    busy: list[tuple[datetime, datetime]],
    day: date,
    tz: ZoneInfo,
) -> Block | None:
    dinner_start = _dt(dinner.start)
    duration = timedelta(minutes=minutes)
    start = dinner_start - duration
    if start < wake:
        return None
    if _overlaps_any(start, dinner_start, busy):
        return None
    return Block(
        id=f"cook-{day.isoformat()}",
        type="cook",
        title="Cook",
        start=start.isoformat(),
        end=dinner_start.isoformat(),
    )


def _place_free(
    day: date,
    minutes: int,
    wake: datetime,
    sleep: datetime,
    busy: list[tuple[datetime, datetime]],
    tz: ZoneInfo,
) -> Block | None:
    duration = timedelta(minutes=minutes)
    evening = (time(18, 0), sleep.time())
    slot = _find_gap(wake, sleep, busy, duration, evening, tz, day, prefer_latest=True)
    if slot is None:
        slot = _find_gap(wake, sleep, busy, duration, (wake.time(), sleep.time()), tz, day, prefer_latest=True)
    if slot is None:
        return None
    start, end = slot
    return Block(
        id=f"free-{day.isoformat()}",
        type="free",
        title="Free time",
        start=start.isoformat(),
        end=end.isoformat(),
    )


def _place_batch_cooks(
    occupied: list[Block],
    settings: Settings,
    tz: ZoneInfo,
    horizon: date,
    day_start: time,
    day_end: time,
) -> list[Block]:
    n = max(1, settings.cooking.batch_per_week)
    scores: list[tuple[int, date]] = []
    for offset in range(settings.horizon_days):
        day = horizon + timedelta(days=offset)
        wake = datetime.combine(day, day_start, tzinfo=tz)
        sleep = datetime.combine(day, day_end, tzinfo=tz)
        busy = _busy_on_day(occupied, wake, sleep)
        free = sum((b - a for a, b in _gaps(wake, sleep, busy)), timedelta())
        scores.append((int(free.total_seconds()), day))
    scores.sort(reverse=True)
    cooks: list[Block] = []
    duration = timedelta(minutes=settings.cooking.cook_minutes)
    for _, day in scores[:n]:
        if any(b.id == f"cook-{day.isoformat()}" for b in occupied):
            continue
        wake = datetime.combine(day, day_start, tzinfo=tz)
        sleep = datetime.combine(day, day_end, tzinfo=tz)
        busy = _busy_on_day(occupied + cooks, wake, sleep)
        dinners = [
            b
            for b in occupied
            if b.type == "meal" and "dinner" in b.title.lower() and _dt(b.start).date() == day
        ]
        slot = None
        if dinners:
            dinner_start = _dt(dinners[0].start)
            start = dinner_start - duration
            if start >= wake and not _overlaps_any(start, dinner_start, busy):
                slot = (start, dinner_start)
        if slot is None:
            slot = _find_gap(wake, sleep, busy, duration, (time(16, 0), time(19, 0)), tz, day)
        if slot is None:
            continue
        start, end = slot
        cooks.append(
            Block(
                id=f"cook-{day.isoformat()}",
                type="cook",
                title="Batch cook",
                start=start.isoformat(),
                end=end.isoformat(),
            )
        )
    return cooks


def _windows_from_occupied(
    occupied: list[Block],
    settings: Settings,
    tz: ZoneInfo,
    horizon: date,
    day_start: time,
    day_end: time,
) -> list[FreeWindow]:
    windows: list[FreeWindow] = []
    for offset in range(settings.horizon_days):
        day = horizon + timedelta(days=offset)
        wake = datetime.combine(day, day_start, tzinfo=tz)
        sleep = datetime.combine(day, day_end, tzinfo=tz)
        busy = _busy_on_day(occupied, wake, sleep)
        for i, (start, end) in enumerate(_gaps(wake, sleep, busy)):
            if end - start < MIN_WINDOW:
                continue
            windows.append(
                FreeWindow(
                    id=f"w-{day.isoformat()}-{i}",
                    start=start.isoformat(),
                    end=end.isoformat(),
                )
            )
    return windows


def _find_gap(
    wake: datetime,
    sleep: datetime,
    busy: list[tuple[datetime, datetime]],
    duration: timedelta,
    window: tuple[time, time],
    tz: ZoneInfo,
    day: date,
    prefer_latest: bool = False,
) -> tuple[datetime, datetime] | None:
    lo = max(wake, datetime.combine(day, window[0], tzinfo=tz))
    hi = min(sleep, datetime.combine(day, window[1], tzinfo=tz))
    if hi <= lo:
        return None
    candidates = [g for g in _gaps(lo, hi, busy) if g[1] - g[0] >= duration]
    if not candidates:
        return None
    start, _end = candidates[-1] if prefer_latest else candidates[0]
    if prefer_latest:
        start = candidates[-1][1] - duration
        if start < candidates[-1][0]:
            start = candidates[-1][0]
    return start, start + duration


def _gaps(
    lo: datetime,
    hi: datetime,
    busy: list[tuple[datetime, datetime]],
) -> list[tuple[datetime, datetime]]:
    clipped: list[tuple[datetime, datetime]] = []
    for a, b in busy:
        start, end = max(a, lo), min(b, hi)
        if end > start:
            clipped.append((start, end))
    clipped.sort()
    merged: list[tuple[datetime, datetime]] = []
    for a, b in clipped:
        if not merged or a > merged[-1][1]:
            merged.append((a, b))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
    gaps: list[tuple[datetime, datetime]] = []
    cursor = lo
    for a, b in merged:
        if a > cursor:
            gaps.append((cursor, a))
        cursor = max(cursor, b)
    if hi > cursor:
        gaps.append((cursor, hi))
    return gaps


def _busy_on_day(
    blocks: list[Block],
    wake: datetime,
    sleep: datetime,
) -> list[tuple[datetime, datetime]]:
    busy: list[tuple[datetime, datetime]] = []
    for block in blocks:
        start, end = _dt(block.start), _dt(block.end)
        if end <= wake or start >= sleep:
            continue
        busy.append((max(start, wake), min(end, sleep)))
    return busy


def _overlaps_any(start: datetime, end: datetime, busy: list[tuple[datetime, datetime]]) -> bool:
    return any(start < b and a < end for a, b in busy)


def _event_block(event: Event) -> Block:
    return Block(
        id=event.id,
        type="event",
        title=event.title,
        start=event.start,
        end=event.end,
        location=event.location,
        locked=True,
    )


def _hhmm(value: str) -> time:
    parts = value.split(":")
    return time(int(parts[0]), int(parts[1]))


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)
