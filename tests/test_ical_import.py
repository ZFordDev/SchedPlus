from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from logic.ical_import import (
    ICalImportError,
    commit_ical_import,
    parse_ical,
    plan_ical_import,
)
from logic.scheduler import Task
from logic.storage import sqlite_storage

GOOGLE_TCAL = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Google Inc//Google Calendar 70.9054//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Example Calendar
BEGIN:VEVENT
DTSTART:20260911T140000Z
DTEND:20260911T153000Z
DTSTAMP:20260901T000000Z
UID:g1@google.com
CREATED:20260901T000000Z
DESCRIPTION:Weekly sync\\nBring the roadmap
LAST-MODIFIED:20260901T000000Z
SEQUENCE:0
STATUS:CONFIRMED
SUMMARY:Team standup
TRANSP:OPAQUE
END:VEVENT
BEGIN:VEVENT
DTSTART;VALUE=DATE:20260912
DTEND;VALUE=DATE:20260913
DTSTAMP:20260901T000000Z
UID:g2@google.com
SEQUENCE:0
SUMMARY:Holiday
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=America/New_York:20260914T100000
DTEND;TZID=America/New_York:20260914T110000
DTSTAMP:20260901T000000Z
UID:g3@google.com
SUMMARY:Call with client
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=America/New_York:20260915T100000
DURATION:PT45M
DTSTAMP:20260901T000000Z
UID:g4@google.com
SUMMARY:Sprint retro
CATEGORIES:Work,Team
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=America/New_York:20260916T100000
DTSTAMP:20260901T000000Z
UID:g5@google.com
SUMMARY:Weekly review
RRULE:FREQ=WEEKLY;COUNT=4
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=America/New_York:20260917T100000
DTSTAMP:20260901T000000Z
UID:g6@google.com
SUMMARY:Old meeting
STATUS:CANCELLED
END:VEVENT
END:VCALENDAR
"""

APPLE_ICAL = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Apple Inc.//macOS 14.0//EN
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:America/Los_Angeles
BEGIN:DAYLIGHT
TZOFFSETFROM:-0800
TZOFFSETTO:-0700
TZNAME:PDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
END:VTIMEZONE
BEGIN:VEVENT
DTSTART;TZID=America/Los_Angeles:20260901T090000
DTEND;TZID=America/Los_Angeles:20260901T093000
UID:a1@apple.com
SUMMARY:Morning workout
DURATION:PT30M
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=America/Los_Angeles:20260902T120000
UID:a2@apple.com
SUMMARY:Dentist
END:VEVENT
BEGIN:VEVENT
DTSTART;VALUE=DATE:20260903
UID:a3@apple.com
SUMMARY:
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=America/Los_Angeles:20260904T150000
UID:a4@apple.com
SUMMARY:Standup
RECURRENCE-ID;TZID=America/Los_Angeles:20260911T150000
END:VEVENT
END:VCALENDAR
"""


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_google_export_maps_timed_event_fields(tmp_path):
    result = parse_ical(
        _write(tmp_path / "google.ics", GOOGLE_TCAL), local_zone=ZoneInfo("UTC")
    )
    events = result.events
    by_text = {event.text: event for event in events}

    standup = by_text["Team standup"]
    assert standup.date == "2026-09-11"
    assert standup.time == "14:00"
    assert standup.notes == "Weekly sync\nBring the roadmap"
    assert standup.duration == "90"
    assert standup.category == ""

    retro = by_text["Sprint retro"]
    assert retro.date == "2026-09-15"
    assert retro.time == "14:00"
    assert retro.duration == "45"
    assert retro.category == "Work, Team"

    call = by_text["Call with client"]
    assert call.date == "2026-09-14"
    assert call.time == "14:00"


def test_google_export_maps_all_day_and_reports_skip_reasons(tmp_path):
    result = parse_ical(
        _write(tmp_path / "google.ics", GOOGLE_TCAL), local_zone=ZoneInfo("UTC")
    )
    by_text = {event.text: event for event in result.events}

    assert by_text["Holiday"].date == "2026-09-12"
    assert by_text["Holiday"].time == "00:00"
    assert by_text["Holiday"].duration == ""

    reasons = {item.text: item.reason for item in result.skipped}
    assert reasons == {"Weekly review": "recurring", "Old meeting": "cancelled"}


def test_apple_export_maps_floating_and_recurrence(tmp_path):
    result = parse_ical(
        _write(tmp_path / "apple.ics", APPLE_ICAL), local_zone=ZoneInfo("UTC")
    )
    by_text = {event.text: event for event in result.events}

    assert by_text["Morning workout"].time == "16:00"
    assert by_text["Morning workout"].date == "2026-09-01"
    assert by_text["Dentist"].date == "2026-09-02"


def test_all_day_and_blank_summary_events_are_handled(tmp_path):
    result = parse_ical(
        _write(tmp_path / "apple.ics", APPLE_ICAL), local_zone=ZoneInfo("UTC")
    )
    by_text = {event.text: event for event in result.events}

    assert by_text["(no title)"].date == "2026-09-03"
    assert by_text["(no title)"].time == "00:00"

    reasons = {item.text: item.reason for item in result.skipped}
    assert "Standup" in reasons
    assert reasons["Standup"] == "recurring"


def test_timezone_conversion_uses_injected_local_zone(tmp_path):
    ics = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART;TZID=America/New_York:20260911T090000
DTEND;TZID=America/New_York:20260911T100000
UID:t1@example.com
SUMMARY:Zone test
END:VEVENT
END:VCALENDAR
"""
    result = parse_ical(
        _write(tmp_path / "tz.ics", ics), local_zone=ZoneInfo("America/New_York")
    )
    event = result.events[0]
    assert event.date == "2026-09-11"
    assert event.time == "09:00"

    utc_result = parse_ical(
        _write(tmp_path / "tz.ics", ics), local_zone=ZoneInfo("UTC")
    )
    assert utc_result.events[0].time == "13:00"


def test_duration_from_dtend_and_duration_property(tmp_path):
    ics = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20260911T100000Z
DTEND:20260911T113000Z
UID:d1@example.com
SUMMARY:By end
END:VEVENT
BEGIN:VEVENT
DTSTART:20260911T120000Z
DURATION:P1DT2H
UID:d2@example.com
SUMMARY:By duration
END:VEVENT
END:VCALENDAR
"""
    result = parse_ical(_write(tmp_path / "dur.ics", ics), local_zone=ZoneInfo("UTC"))
    by_text = {event.text: event for event in result.events}
    assert by_text["By end"].duration == "90"
    assert by_text["By duration"].duration == "1560"


def test_description_escapes_are_decoded(tmp_path):
    ics = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20260911T100000Z
UID:e1@example.com
SUMMARY:Escapes \\, here
DESCRIPTION:Line one\\nLine two \\; done
END:VEVENT
END:VCALENDAR
"""
    result = parse_ical(_write(tmp_path / "esc.ics", ics), local_zone=ZoneInfo("UTC"))
    event = result.events[0]
    assert event.text == "Escapes , here"
    assert event.notes == "Line one\nLine two ; done"


def test_parse_raises_for_missing_file(tmp_path):
    with pytest.raises(ICalImportError, match="Unable to read"):
        parse_ical(tmp_path / "missing.ics")


def test_parse_raises_for_invalid_content(tmp_path):
    with pytest.raises(ICalImportError, match="not a valid iCalendar"):
        parse_ical(_write(tmp_path / "bad.ics", "not an ical file"))


def test_plan_counts_duplicates_by_content(tmp_path):
    existing = [
        Task(date="2026-09-11", time="14:00", text="Team standup"),
        Task(date="2026-09-12", time="00:00", text="Holiday"),
    ]
    plan = plan_ical_import(
        _write(tmp_path / "google.ics", GOOGLE_TCAL),
        existing,
        local_zone=ZoneInfo("UTC"),
    )

    assert plan.ready == 2
    assert plan.duplicates == 2
    assert [item.reason for item in plan.skipped] == ["recurring", "cancelled"]
    assert plan.event_count == 6


def test_plan_deduplicates_within_a_file(tmp_path):
    ics = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20260911T100000Z
UID:x1@example.com
SUMMARY:Twice
END:VEVENT
BEGIN:VEVENT
DTSTART:20260911T100000Z
UID:x2@example.com
SUMMARY:Twice
END:VEVENT
END:VCALENDAR
"""
    plan = plan_ical_import(
        _write(tmp_path / "dup.ics", ics), [], local_zone=ZoneInfo("UTC")
    )

    assert plan.ready == 1
    assert plan.duplicates == 1


def test_plan_event_count_includes_skipped(tmp_path):
    plan = plan_ical_import(
        _write(tmp_path / "google.ics", GOOGLE_TCAL), [], local_zone=ZoneInfo("UTC")
    )

    assert plan.event_count == 6
    assert plan.ready == 4
    assert plan.duplicates == 0
    assert len(plan.skipped) == 2


@pytest.fixture
def database(monkeypatch, tmp_path):
    path = tmp_path / "data" / "tasks.db"
    path.parent.mkdir()
    monkeypatch.setattr(sqlite_storage, "prepare_database", lambda: path)
    monkeypatch.setattr(sqlite_storage, "_configure_logging", lambda _directory: None)
    sqlite_storage.initialize_database()
    return path


def test_commit_inserts_planned_tasks_into_storage(database, tmp_path):
    plan = plan_ical_import(
        _write(tmp_path / "google.ics", GOOGLE_TCAL), [], local_zone=ZoneInfo("UTC")
    )

    count = commit_ical_import(plan.tasks)

    assert count == 4
    stored = sqlite_storage.list_entries()
    assert len(stored) == 4
    assert {task.text for task in stored} == {
        "Team standup",
        "Holiday",
        "Call with client",
        "Sprint retro",
    }


def test_commit_empty_plan_is_a_no_op(database):
    assert commit_ical_import([]) == 0
    assert sqlite_storage.list_entries() == []


def test_end_to_end_google_and_apple_imports(tmp_path, database):
    google_plan = plan_ical_import(
        _write(tmp_path / "google.ics", GOOGLE_TCAL), [], local_zone=ZoneInfo("UTC")
    )
    apple_plan = plan_ical_import(
        _write(tmp_path / "apple.ics", APPLE_ICAL), [], local_zone=ZoneInfo("UTC")
    )

    google_count = commit_ical_import(google_plan.tasks)
    apple_count = commit_ical_import(apple_plan.tasks)

    assert google_count == 4
    assert apple_count == 3
    stored = sqlite_storage.list_entries()
    assert len(stored) == 7
    assert date.fromisoformat(stored[0].date).year == 2026
