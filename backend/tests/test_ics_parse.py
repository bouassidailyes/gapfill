from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from app.ics_parse import IcsParseError, parse_ics

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "fixtures" / "sample_calendar.ics"


def test_parse_sample_calendar_has_recurring_all_day_and_locations() -> None:
    events = parse_ics(
        SAMPLE.read_bytes(),
        horizon_start=date(2026, 9, 21),
        horizon_days=8,
    )
    titles = {e.title for e in events}
    assert "Databases lecture" in titles
    assert "Study association day" in titles
    locations = {e.location for e in events if e.location}
    assert "UM Campus" in locations
    assert "University Library" in locations
    lectures = [e for e in events if e.title == "Databases lecture"]
    assert len(lectures) >= 3
    all_day = next(e for e in events if e.title == "Study association day")
    assert all_day.start.startswith("2026-09-26")


def test_bad_ics_raises() -> None:
    with pytest.raises(IcsParseError):
        parse_ics(b"this is not a calendar")
