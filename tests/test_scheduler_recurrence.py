from dataclasses import replace
from datetime import datetime

import pytest

from logic.scheduler import Scheduler
from logic.storage import sqlite_storage as storage


@pytest.fixture
def database(monkeypatch, tmp_path):
    path = tmp_path / "data" / "tasks.db"
    path.parent.mkdir()
    monkeypatch.setattr(storage, "prepare_database", lambda: path)
    monkeypatch.setattr(storage, "_configure_logging", lambda _directory: None)
    return path


@pytest.fixture
def scheduler(database):
    storage.initialize_database()
    return Scheduler()


class _FrozenDateTime(datetime):
    """Drop-in datetime whose now() never moves; recurrence math ignores it."""

    @classmethod
    def now(cls, tz=None):
        return cls(2026, 2, 1, 12, 0, 0)


@pytest.fixture
def frozen_clock(monkeypatch):
    monkeypatch.setattr("logic.scheduler.datetime", _FrozenDateTime)


def _with_recurrence(scheduler, task, recurrence, end=""):
    updated = replace(task, recurrence=recurrence, recurrenceEnd=end)
    scheduler.update_task(updated)
    return updated


def test_monthly_recurrence_clamps_to_last_valid_day(scheduler, frozen_clock):
    task = scheduler.add_task(date="2026-01-31", time="09:00", text="Rent day")
    _with_recurrence(scheduler, task, "monthly")

    scheduler.complete_task(task.id)

    assert "2026-02-28" in [t.date for t in scheduler.get_tasks()]
    assert "2026-01-31" not in [
        t.date for t in scheduler.get_tasks() if t.id != task.id
    ]


def test_monthly_recurrence_wraps_year_boundary(scheduler, frozen_clock):
    task = scheduler.add_task(date="2026-12-31", time="09:00", text="Year end")
    _with_recurrence(scheduler, task, "monthly")

    scheduler.complete_task(task.id)

    assert "2027-01-31" in [t.date for t in scheduler.get_tasks()]


def test_monthly_recurrence_keeps_day_when_target_month_allows_it(
    scheduler, frozen_clock
):
    task = scheduler.add_task(date="2026-01-15", time="09:00", text="Mid month")
    _with_recurrence(scheduler, task, "monthly")

    scheduler.complete_task(task.id)

    assert "2026-02-15" in [t.date for t in scheduler.get_tasks()]


def test_yearly_recurrence_clamps_feb29_into_non_leap_year(scheduler, frozen_clock):
    task = scheduler.add_task(date="2028-02-29", time="09:00", text="Leap day")
    _with_recurrence(scheduler, task, "yearly")

    scheduler.complete_task(task.id)

    assert "2029-02-28" in [t.date for t in scheduler.get_tasks()]


def test_daily_and_weekly_recurrence_advance_by_full_periods(scheduler, frozen_clock):
    daily = scheduler.add_task(date="2026-08-20", time="09:00", text="Daily")
    weekly = scheduler.add_task(date="2026-08-20", time="10:00", text="Weekly")
    _with_recurrence(scheduler, daily, "daily")
    _with_recurrence(scheduler, weekly, "weekly")

    scheduler.complete_task(daily.id)
    scheduler.complete_task(weekly.id)

    dates = [t.date for t in scheduler.get_tasks()]
    assert "2026-08-21" in dates
    assert "2026-08-27" in dates


def test_recurrence_stops_at_end_date(scheduler, frozen_clock):
    task = scheduler.add_task(date="2026-01-31", time="09:00", text="Bounded")
    _with_recurrence(scheduler, task, "monthly", end="2026-01-31")

    scheduler.complete_task(task.id)

    assert len(scheduler.get_tasks()) == 1


def test_new_occurrence_is_uncompleted_and_persisted(scheduler, frozen_clock):
    task = scheduler.add_task(date="2026-08-20", time="09:00", text="Chain")
    _with_recurrence(scheduler, task, "weekly")

    scheduler.complete_task(task.id)

    stored = {t.text: t for t in storage.list_entries()}
    successor = [t for t in stored.values() if t.date == "2026-08-27"]
    assert len(successor) == 1
    assert successor[0].completed == ""
    assert successor[0].id != task.id
    assert storage.list_completed_entries()[0].id == task.id


def test_completed_entries_carry_optional_fields(scheduler):
    task = scheduler.add_task(date="2026-08-20", time="10:00", text="Rich task")
    rich = replace(
        task,
        notes="note",
        priority="high",
        duration="45",
        category="Work",
        reminder="30",
    )
    scheduler.update_task(rich)
    scheduler.complete_task(rich.id)

    completed = storage.list_completed_entries()
    match = next(t for t in completed if t.text == "Rich task")

    assert match.completed == "true"
    assert match.notes == "note"
    assert match.priority == "high"
    assert match.duration == "45"
    assert match.category == "Work"
    assert match.reminder == "30"
