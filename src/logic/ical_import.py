# SPDX-License-Identifier: Apache-2.0

"""Offline iCalendar (.ics) event import mapped onto SchedPlus tasks.

The import pipeline is split into three phases so callers can preview an
import and cancel before any database change:

1. ``plan_ical_import`` parses the file and plans what would be inserted
   without touching storage.
2. The caller shows the plan (preview / dry run).
3. ``commit_ical_import`` inserts the confirmed tasks.

Mapping policy
--------------
==============  =============================================================
iCal property   Task field
==============  =============================================================
SUMMARY         text (falls back to "(no title)" when absent)
DESCRIPTION     notes
CATEGORIES      category (multiple categories joined with ", ")
DTSTART         date and, for timed events, time
DTEND / DURATION  duration (positive integer minutes, "" when none)
==============  =============================================================

Timed events are converted to the local wall clock: UTC and TZID aware
start times are shifted into the user's timezone before their date and
time are stored.  All-day events (``VALUE=DATE``) map to ``00:00`` on
their date because SchedPlus tasks always carry a time.

Duplicate detection uses the task content key ``(date, time, text)``,
matching what a user would recognise as the same event on a repeated
import.  Full iCalendar recurrence (``RRULE``, ``RDATE``,
``RECURRENCE-ID``) is deliberately unsupported in this first version:
those events are counted and reported rather than silently dropped.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, tzinfo
from pathlib import Path
from zoneinfo import ZoneInfo

from .data_transfer import DataTransferError
from .scheduler import Task
from .storage import sqlite_storage
from .validation import ValidationError, validate_task

ALL_DAY_DEFAULT_TIME = "00:00"
NO_TITLE = "(no title)"
RECURRENCE_PROPERTIES = ("RRULE", "RDATE", "RECURRENCE-ID")


class ICalImportError(DataTransferError):
    """An unreadable, malformed, or unsupported local iCalendar file."""


@dataclass(frozen=True)
class ICSEvent:
    """A normalized event candidate mapped into SchedPlus task fields."""

    date: str
    time: str
    text: str
    notes: str = ""
    category: str = ""
    duration: str = ""


@dataclass(frozen=True)
class SkippedEvent:
    """A calendar event that will not be imported, with the reason."""

    text: str
    reason: str


@dataclass(frozen=True)
class ICSParseResult:
    events: list[ICSEvent]
    skipped: list[SkippedEvent]


@dataclass(frozen=True)
class ICSImportPlan:
    """The preview of an .ics import, without any storage change."""

    tasks: list[Task]
    duplicates: int
    skipped: list[SkippedEvent]
    event_count: int

    @property
    def ready(self) -> int:
        """The number of events ready to import."""
        return len(self.tasks)


def plan_ical_import(
    path: Path, existing_tasks: list[Task], *, local_zone: tzinfo | None = None
) -> ICSImportPlan:
    """Parse a local .ics file and plan the import without touching storage."""
    result = parse_ical(path, local_zone=local_zone)
    existing_keys = {(task.date, task.time, task.text) for task in existing_tasks}
    tasks: list[Task] = []
    duplicates = 0
    invalid: list[SkippedEvent] = []

    for event in result.events:
        try:
            task = validate_task(
                Task(
                    date=event.date,
                    time=event.time,
                    text=event.text,
                    notes=event.notes,
                    category=event.category,
                    duration=event.duration,
                )
            )
        except ValidationError:
            invalid.append(SkippedEvent(event.text, "invalid event data"))
            continue
        key = (task.date, task.time, task.text)
        if key in existing_keys:
            duplicates += 1
            continue
        existing_keys.add(key)
        tasks.append(task)

    return ICSImportPlan(
        tasks=tasks,
        duplicates=duplicates,
        skipped=[*result.skipped, *invalid],
        event_count=len(result.events) + len(result.skipped),
    )


def parse_ical(path: Path, *, local_zone: tzinfo | None = None) -> ICSParseResult:
    """Parse a local .ics file into normalized event candidates."""
    calendar = _load_calendar(path)
    zone = local_zone or _system_local_zone()
    events: list[ICSEvent] = []
    skipped: list[SkippedEvent] = []

    for component in calendar.walk():
        if getattr(component, "name", "") != "VEVENT":
            continue
        converted = _convert_event(component, zone)
        if isinstance(converted, SkippedEvent):
            skipped.append(converted)
        else:
            events.append(converted)

    return ICSParseResult(events, skipped)


def commit_ical_import(tasks: list[Task]) -> int:
    """Insert the confirmed tasks in one transaction and return the count."""
    imported, _duplicates, _conflicts = sqlite_storage.import_entries(tasks)
    return imported


def _load_calendar(path: Path):
    try:
        content = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise ICalImportError(f"Unable to read {path}: {exc}") from exc

    try:
        from icalendar import Calendar
    except ImportError as exc:
        raise ICalImportError(
            "iCalendar import requires the 'icalendar' package to be installed."
        ) from exc

    try:
        return Calendar.from_ical(content)
    except (TypeError, ValueError, AttributeError) as exc:
        raise ICalImportError(f"This is not a valid iCalendar file: {exc}") from exc


def _system_local_zone() -> tzinfo:
    local = datetime.now().astimezone().tzinfo
    if local is None:
        return ZoneInfo("UTC")
    key = getattr(local, "key", None)
    return ZoneInfo(key) if key else local


def _convert_event(component, zone: tzinfo) -> ICSEvent | SkippedEvent:
    summary = _component_text(component.get("SUMMARY"), NO_TITLE)
    if _component_text(component.get("STATUS"), "").upper() == "CANCELLED":
        return SkippedEvent(summary, "cancelled")
    if any(component.get(name) is not None for name in RECURRENCE_PROPERTIES):
        return SkippedEvent(summary, "recurring")
    start = component.get("DTSTART")
    if start is None:
        return SkippedEvent(summary, "missing start date")

    date_text, time_text, duration = _start_details(start, component, zone)
    return ICSEvent(
        date=date_text,
        time=time_text,
        text=summary,
        notes=_component_text(component.get("DESCRIPTION"), ""),
        category=_category_text(component),
        duration=duration,
    )


def _start_details(start, component, zone: tzinfo):
    value = start.dt
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(zone)
        return (
            value.date().isoformat(),
            value.strftime("%H:%M"),
            _event_duration(component, value),
        )
    return value.isoformat(), ALL_DAY_DEFAULT_TIME, ""


def _event_duration(component, start_value) -> str:
    end = component.get("DTEND")
    if end is not None:
        try:
            return _duration_minutes(end.dt - start_value)
        except (TypeError, ValueError):
            return ""
    duration = component.get("DURATION")
    if duration is not None:
        return _duration_minutes(duration.dt)
    return ""


def _duration_minutes(delta) -> str:
    if not isinstance(delta, timedelta):
        return ""
    minutes = int(delta.total_seconds() // 60)
    return str(minutes) if minutes > 0 else ""


def _component_text(value, default: str) -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _category_text(component) -> str:
    categories = component.get("CATEGORIES")
    if not categories:
        return ""
    values = [str(item).strip() for item in categories]
    return ", ".join(value for value in values if value)
