"""Parse a timetable .csv export into Event[] (architecture.md §5 step 1)."""

from __future__ import annotations

import csv
import io
from datetime import date, datetime, time, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

from app.models import Event

DEFAULT_TIMEZONE = "Europe/Amsterdam"

# Header aliases, lowercased. Covers the Google Calendar and Outlook CSV exports
# plus the wording university timetable tools tend to use.
COLUMNS: dict[str, tuple[str, ...]] = {
    "title": ("subject", "title", "summary", "event", "name", "description", "course"),
    "start_date": ("start date", "startdate", "date", "start day", "begin date"),
    "start_time": ("start time", "starttime", "start", "from", "begin time"),
    "end_date": ("end date", "enddate", "finish date"),
    "end_time": ("end time", "endtime", "end", "to", "finish time"),
    "location": ("location", "room", "building", "venue", "where"),
    "all_day": ("all day event", "all day", "allday"),
}

DATE_FORMATS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
)

TIME_FORMATS = ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p", "%H.%M")

DEFAULT_EVENT_MINUTES = 60


class CsvParseError(ValueError):
    """Raised when the file is not a usable timetable export."""


def parse_csv(
    data: bytes,
    timezone: str = DEFAULT_TIMEZONE,
) -> list[Event]:
    tz = ZoneInfo(timezone)
    text = _decode(data)
    reader = csv.DictReader(io.StringIO(text), dialect=_sniff(text))

    if not reader.fieldnames:
        raise CsvParseError("This file has no column headers.")

    mapping = _map_columns(reader.fieldnames)
    if "title" not in mapping or "start_date" not in mapping:
        raise CsvParseError(
            "Could not find a title and a start date column. "
            "Expected headers like 'Subject', 'Start Date', 'Start Time', 'Location'."
        )

    events: list[Event] = []
    for index, row in enumerate(reader):
        event = _row_to_event(row, mapping, tz, index)
        if event is not None:
            events.append(event)

    if not events:
        raise CsvParseError("No events found in this file.")

    events.sort(key=lambda e: e.start)
    return events


def _decode(data: bytes) -> str:
    if not data.strip():
        raise CsvParseError("The uploaded file is empty.")
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise CsvParseError("Could not read this file as text.")


def _sniff(text: str) -> type[csv.Dialect] | csv.Dialect:
    sample = text[:4096]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def _map_columns(fieldnames: list[str | None]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for raw in fieldnames:
        if raw is None:
            continue
        normalised = raw.strip().lower()
        for field, aliases in COLUMNS.items():
            if field in mapping:
                continue
            if normalised in aliases:
                mapping[field] = raw
                break
    return mapping


def _row_to_event(
    row: dict[str, str | None],
    mapping: dict[str, str],
    tz: ZoneInfo,
    index: int,
) -> Event | None:
    title = _cell(row, mapping.get("title"))
    start_date = _parse_date(_cell(row, mapping.get("start_date")))
    if not title or start_date is None:
        return None

    all_day = _is_truthy(_cell(row, mapping.get("all_day")))
    start_time = _parse_time(_cell(row, mapping.get("start_time")))
    end_time = _parse_time(_cell(row, mapping.get("end_time")))
    end_date = _parse_date(_cell(row, mapping.get("end_date"))) or start_date

    if all_day or (start_time is None and end_time is None):
        start_dt = datetime.combine(start_date, time.min, tzinfo=tz)
        end_dt = datetime.combine(end_date, time.min, tzinfo=tz) + timedelta(days=1)
    else:
        start_dt = datetime.combine(start_date, start_time or time.min, tzinfo=tz)
        if end_time is None:
            end_dt = start_dt + timedelta(minutes=DEFAULT_EVENT_MINUTES)
        else:
            end_dt = datetime.combine(end_date, end_time, tzinfo=tz)
        # An end before the start means the event runs past midnight.
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

    location = _cell(row, mapping.get("location"))

    return Event(
        id=f"csv-{index}-{start_dt.strftime('%Y%m%dT%H%M%S')}-{uuid4().hex[:6]}",
        title=title,
        start=start_dt.isoformat(),
        end=end_dt.isoformat(),
        location=location or None,
    )


def _cell(row: dict[str, str | None], key: str | None) -> str:
    if key is None:
        return ""
    value = row.get(key)
    return value.strip() if isinstance(value, str) else ""


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"true", "yes", "y", "1"}


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_time(value: str) -> time | None:
    if not value:
        return None
    cleaned = value.replace("u", ":").strip()
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).time()
        except ValueError:
            continue
    return None
