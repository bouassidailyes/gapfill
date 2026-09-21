"""Block[] → .ics bytes (architecture.md §5 step 6)."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event as IcsEvent

from app.models import Block

PRODID = "-//Gapfill//AI Student Scheduler//EN"

# Times go out as UTC. A fixed-offset TZID like "UTC+02:00" is not a real zone
# and needs a VTIMEZONE block; plain UTC imports cleanly everywhere.
FALLBACK_TIMEZONE = ZoneInfo("Europe/Amsterdam")

# Blocks that came from the student's own calendar. Excluded by default so
# importing the export doesn't duplicate events they already have.
FIXED_TYPES = {"event"}

# Dropped either way: slack is padding between blocks, not a real appointment.
SKIP_TYPES = {"slack"}


class IcsExportError(ValueError):
    """Raised when a block cannot be turned into a calendar entry."""


def blocks_to_ics(blocks: list[Block], include_fixed: bool = False) -> bytes:
    calendar = Calendar()
    calendar.add("prodid", PRODID)
    calendar.add("version", "2.0")
    calendar.add("calscale", "GREGORIAN")
    calendar.add("x-wr-calname", "Gapfill plan")

    stamp = datetime.now().astimezone()

    for block in blocks:
        if block.type in SKIP_TYPES:
            continue
        if not include_fixed and block.type in FIXED_TYPES:
            continue

        entry = IcsEvent()
        entry.add("uid", f"{block.id}@gapfill")
        entry.add("summary", block.title)
        entry.add("dtstart", _parse(block.start, block.title))
        entry.add("dtend", _parse(block.end, block.title))
        entry.add("dtstamp", stamp)
        entry.add("categories", [block.type])
        if block.location:
            entry.add("location", block.location)
        calendar.add_component(entry)

    return calendar.to_ical()


def _parse(value: str, title: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise IcsExportError(f"Block '{title}' has an unreadable time: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=FALLBACK_TIMEZONE)
    return parsed.astimezone(timezone.utc)
