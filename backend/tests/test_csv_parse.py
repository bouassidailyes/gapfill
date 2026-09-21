from __future__ import annotations

import pytest

from app.csv_parse import CsvParseError, parse_csv

GOOGLE_STYLE = (
    "Subject,Start Date,Start Time,End Date,End Time,All Day Event,Location\r\n"
    "Databases lecture,2026-09-21,09:00,2026-09-21,11:00,False,UM Campus\r\n"
    "Statistics tutorial,2026-09-22,14:00,2026-09-22,16:00,False,University Library\r\n"
    "Study association day,2026-09-26,,,,True,UM Campus\r\n"
).encode("utf-8")


def test_parses_times_locations_and_sorts() -> None:
    events = parse_csv(GOOGLE_STYLE)

    assert [e.title for e in events] == [
        "Databases lecture",
        "Statistics tutorial",
        "Study association day",
    ]
    assert events[0].start == "2026-09-21T09:00:00+02:00"
    assert events[0].end == "2026-09-21T11:00:00+02:00"
    assert events[0].location == "UM Campus"


def test_all_day_event_spans_the_whole_day() -> None:
    all_day = parse_csv(GOOGLE_STYLE)[2]

    assert all_day.start == "2026-09-26T00:00:00+02:00"
    assert all_day.end == "2026-09-27T00:00:00+02:00"


def test_accepts_semicolons_dmy_dates_and_alternative_headers() -> None:
    data = (
        "Course;Date;From;To;Room\r\n"
        "HCI lab;24/09/2026;13:00;15:00;UM Campus\r\n"
    ).encode("utf-8")

    events = parse_csv(data)

    assert len(events) == 1
    assert events[0].title == "HCI lab"
    assert events[0].start == "2026-09-24T13:00:00+02:00"
    assert events[0].end == "2026-09-24T15:00:00+02:00"
    assert events[0].location == "UM Campus"


def test_event_past_midnight_rolls_to_the_next_day() -> None:
    data = (
        "Subject,Start Date,Start Time,End Time\r\n"
        "Night shift,2026-09-21,22:00,02:00\r\n"
    ).encode("utf-8")

    events = parse_csv(data)

    assert events[0].start == "2026-09-21T22:00:00+02:00"
    assert events[0].end == "2026-09-22T02:00:00+02:00"


def test_missing_end_time_defaults_to_one_hour() -> None:
    data = ("Subject,Start Date,Start Time\r\nOffice hours,2026-09-21,10:00\r\n").encode("utf-8")

    events = parse_csv(data)

    assert events[0].end == "2026-09-21T11:00:00+02:00"


def test_rows_without_a_title_or_date_are_skipped() -> None:
    data = (
        "Subject,Start Date,Start Time\r\n"
        ",2026-09-21,10:00\r\n"
        "Real lecture,2026-09-21,12:00\r\n"
    ).encode("utf-8")

    assert [e.title for e in parse_csv(data)] == ["Real lecture"]


def test_unrecognised_headers_raise() -> None:
    with pytest.raises(CsvParseError, match="title and a start date"):
        parse_csv(b"foo,bar\r\n1,2\r\n")


def test_empty_file_raises() -> None:
    with pytest.raises(CsvParseError):
        parse_csv(b"")


def test_headers_but_no_usable_rows_raise() -> None:
    with pytest.raises(CsvParseError, match="No events"):
        parse_csv(b"Subject,Start Date\r\n,\r\n")
