import pytest

from logic.scheduler import Scheduler, Task
from logic.storage import sqlite_storage
from logic.validation import ValidationError, validate_task


def test_validate_task_accepts_and_normalizes_valid_values():
    task = Task(date=" 2026-08-12 ", time=" 09:05 ", text=" Plan release ")

    assert validate_task(task) is task
    assert (task.date, task.time, task.text) == (
        "2026-08-12",
        "09:05",
        "Plan release",
    )


@pytest.mark.parametrize("date", ["", "12-08-2026", "2026-8-12", "2026-02-30"])
def test_validate_task_rejects_invalid_dates(date):
    with pytest.raises(ValidationError, match="YYYY-MM-DD"):
        validate_task(Task(date=date, time="09:05", text="Plan release"))


@pytest.mark.parametrize("time", ["", "9:05", "09.05", "24:00", "12:60"])
def test_validate_task_rejects_invalid_times(time):
    with pytest.raises(ValidationError, match="HH:MM"):
        validate_task(Task(date="2026-08-12", time=time, text="Plan release"))


@pytest.mark.parametrize("text", ["", "   ", "\t\n"])
def test_validate_task_rejects_empty_text(text):
    with pytest.raises(ValidationError, match="cannot be empty"):
        validate_task(Task(date="2026-08-12", time="09:05", text=text))


def test_scheduler_does_not_persist_invalid_tasks(monkeypatch):
    persisted = []
    monkeypatch.setattr(sqlite_storage, "create_entry", persisted.append)

    with pytest.raises(ValidationError):
        Scheduler().add_task("2026-02-30", "09:05", "Invalid date")

    assert persisted == []


def test_scheduler_persists_normalized_task(monkeypatch):
    persisted = []
    monkeypatch.setattr(sqlite_storage, "create_entry", persisted.append)

    task = Scheduler().add_task(" 2026-08-12 ", " 09:05 ", " Plan release ")

    assert persisted == [task]
    assert (task.date, task.time, task.text) == (
        "2026-08-12",
        "09:05",
        "Plan release",
    )


def test_scheduler_does_not_update_invalid_task(monkeypatch):
    persisted = []
    monkeypatch.setattr(sqlite_storage, "update_entry", persisted.append)
    task = Task(date="2026-08-12", time="99:99", text="Invalid time")

    with pytest.raises(ValidationError):
        Scheduler().update_task(task)

    assert persisted == []
