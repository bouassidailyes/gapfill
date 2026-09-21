"""Parse an .ics file into Event[] (architecture.md §5 step 1)."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

import recurring_ical_events
from icalendar import Calendar

from app.models import Event

DEFAULT_TIMEZONE = "Europe/Amsterdam"
DEFAULT_HORIZON_DAYS = 14


class IcsParseError(ValueError):
    """Raised when the file is not a usable calendar."""


def parse_ics(
    data: bytes,
    timezone: str = DEFAULT_TIMEZONE,
    horizon_start: date | None = None,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
) -> list[Event]:
    tz = ZoneInfo(timezone)
    start_day = horizon_start or datetime.now(tz).date()
    window_start = datetime.combine(start_day, time.min, tzinfo=tz)
    window_end = window_start + timedelta(days=horizon_days)

    try:
        calendar = Calendar.from_ical(data)
    except Exception as exc:
        raise IcsParseError("This file is not a valid .ics calendar.") from exc

    if calendar is None:
        raise IcsParseError("This file is not a valid .ics calendar.")

    try:
        occurrences = recurring_ical_events.of(calendar).between(window_start, window_end)
    except Exception as exc:
        raise IcsParseError("Could not expand events from this calendar.") from exc

    events: list[Event] = []
    for component in occurrences:
        start_raw = component.get("DTSTART")
        if start_raw is None:
            continue
        start_dt = _to_aware(_unwrap(start_raw), tz)
        end_raw = component.get("DTEND")
        if end_raw is not None:
            end_dt = _to_aware(_unwrap(end_raw), tz)
        else:
            duration = component.get("DURATION")
            if duration is not None:
                end_dt = start_dt + _unwrap(duration)
            elif isinstance(_unwrap(start_raw), date) and not isinstance(_unwrap(start_raw), datetime):
                end_dt = start_dt + timedelta(days=1)
            else:
                end_dt = start_dt + timedelta(hours=1)

        uid = str(component.get("UID") or uuid4())
        summary = str(component.get("SUMMARY") or "Untitled")
        location_val = component.get("LOCATION")
        location = str(location_val) if location_val else None
        event_id = f"{uid}-{start_dt.strftime('%Y%m%dT%H%M%S')}"
        events.append(
            Event(
                id=event_id,
                title=summary,
                start=start_dt.isoformat(),
                end=end_dt.isoformat(),
                location=location,
            )
        )

    events.sort(key=lambda e: e.start)
    return events


def _unwrap(value: object) -> object:
    dt = getattr(value, "dt", None)
    if dt is not None:
        return dt
    return value


def _to_aware(value: object, tz: ZoneInfo) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=tz)
        return value.astimezone(tz)
    if isinstance(value, date):
        return datetime.combine(value, time.min, tzinfo=tz)
    raise IcsParseError("An event is missing a usable start or end time.")
