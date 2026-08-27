"""Helpers for SchedPlus local wall-clock dates and times."""

from datetime import date, datetime, time


def now() -> datetime:
    """Return the current local time as a timezone-aware datetime."""
    return datetime.now().astimezone()


def today() -> date:
    """Return the current date in the users local timezone."""
    return now().date()


def combine(date_text: str, time_text: str) -> datetime:
    """Interpret stored date and time strings in the local timezone."""
    wall_clock = datetime.combine(
        date.fromisoformat(date_text),
        time.fromisoformat(time_text),
    )
    return wall_clock.astimezone()
