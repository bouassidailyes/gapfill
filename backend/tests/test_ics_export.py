from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from icalendar import Calendar

from app.ics_export import IcsExportError, blocks_to_ics
from app.models import Block

BLOCKS = [
    Block(
        id="ev-1",
        type="event",
        title="Databases lecture",
        start="2026-09-21T09:00:00+02:00",
        end="2026-09-21T11:00:00+02:00",
        location="UM Campus",
    ),
    Block(
        id="t-1",
        type="task",
        title="Finish DB assignment",
        start="2026-09-21T13:00:00+02:00",
        end="2026-09-21T14:30:00+02:00",
        task_id="t1",
    ),
    Block(
        id="m-1",
        type="meal",
        title="Lunch",
        start="2026-09-21T12:00:00+02:00",
        end="2026-09-21T12:30:00+02:00",
    ),
    Block(
        id="s-1",
        type="slack",
        title="Slack",
        start="2026-09-21T14:30:00+02:00",
        end="2026-09-21T14:45:00+02:00",
    ),
]


def _summaries(payload: bytes) -> list[str]:
    calendar = Calendar.from_ical(payload)
    return [str(c.get("SUMMARY")) for c in calendar.walk("VEVENT")]


def test_excludes_original_events_and_slack_by_default() -> None:
    summaries = _summaries(blocks_to_ics(BLOCKS))

    assert summaries == ["Finish DB assignment", "Lunch"]


def test_include_fixed_adds_the_students_own_events() -> None:
    summaries = _summaries(blocks_to_ics(BLOCKS, include_fixed=True))

    assert "Databases lecture" in summaries
    assert "Slack" not in summaries


def test_times_location_and_category_survive_the_round_trip() -> None:
    calendar = Calendar.from_ical(blocks_to_ics(BLOCKS, include_fixed=True))
    lecture = next(c for c in calendar.walk("VEVENT") if str(c.get("SUMMARY")) == "Databases lecture")

    amsterdam = ZoneInfo("Europe/Amsterdam")
    assert lecture["DTSTART"].dt == datetime(2026, 9, 21, 9, 0, tzinfo=amsterdam)
    assert lecture["DTEND"].dt == datetime(2026, 9, 21, 11, 0, tzinfo=amsterdam)
    assert str(lecture.get("LOCATION")) == "UM Campus"
    assert lecture.get("CATEGORIES").cats == ["event"]


def test_times_are_written_as_utc_so_calendars_import_them_correctly() -> None:
    payload = blocks_to_ics(BLOCKS).decode()

    assert "DTSTART:20260921T110000Z" in payload
    assert "TZID" not in payload


def test_uids_are_stable_across_exports() -> None:
    first = Calendar.from_ical(blocks_to_ics(BLOCKS))
    second = Calendar.from_ical(blocks_to_ics(BLOCKS))

    assert [str(c.get("UID")) for c in first.walk("VEVENT")] == [
        str(c.get("UID")) for c in second.walk("VEVENT")
    ]


def test_unreadable_time_raises() -> None:
    broken = [Block(id="b", type="task", title="Broken", start="not-a-time", end="also-not")]

    with pytest.raises(IcsExportError, match="unreadable time"):
        blocks_to_ics(broken)
