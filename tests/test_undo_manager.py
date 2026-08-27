import pytest

from logic.scheduler import Task
from logic.storage import sqlite_storage as storage
from logic.undo_manager import UndoManager


class RecordingScheduler:
    def __init__(self):
        self.tasks = []
        self.deleted = []
        self.updated = []
        self.completed = []
        self.uncompleted = []

    def delete_task(self, task_id):
        self.deleted.append(task_id)

    def update_task(self, task):
        self.updated.append(task)

    def complete_task(self, task_id):
        self.completed.append(task_id)

    def uncomplete_task(self, task_id):
        self.uncompleted.append(task_id)


class FailingScheduler:
    def delete_task(self, _task_id):
        raise RuntimeError("storage unavailable")


def test_successful_undo_consumes_action():
    scheduler = RecordingScheduler()
    manager = UndoManager(scheduler)
    manager.record_add("task-1")

    assert manager.undo() == "Undid add"
    assert scheduler.deleted == ["task-1"]
    assert not manager.can_undo()


def test_undo_delete_restores_original_task(monkeypatch):
    scheduler = RecordingScheduler()
    manager = UndoManager(scheduler)
    task = Task(id="task-1", date="2026-08-28", time="09:00", text="Restore me")
    restored = []
    monkeypatch.setattr(storage, "create_entry", restored.append)
    manager.record_delete(task)

    assert manager.undo() == "Undid delete"
    assert restored == [task]
    assert scheduler.tasks == [task]


def test_undo_edit_restores_snapshot():
    scheduler = RecordingScheduler()
    manager = UndoManager(scheduler)
    snapshot = Task(id="task-1", date="2026-08-28", time="09:00", text="Before")
    manager.record_edit(snapshot)

    assert manager.undo() == "Undid edit"
    assert scheduler.updated == [snapshot]


@pytest.mark.parametrize(
    ("record_method", "expected_result", "recorded_attribute"),
    [
        ("record_complete", "Undid complete", "uncompleted"),
        ("record_uncomplete", "Undid uncomplete", "completed"),
    ],
)
def test_undo_completion_state(record_method, expected_result, recorded_attribute):
    scheduler = RecordingScheduler()
    manager = UndoManager(scheduler)
    getattr(manager, record_method)("task-1")

    assert manager.undo() == expected_result
    assert getattr(scheduler, recorded_attribute) == ["task-1"]


def test_undo_empty_history_returns_none():
    assert UndoManager(RecordingScheduler()).undo() is None


def test_history_limit_drops_oldest_actions():
    scheduler = RecordingScheduler()
    manager = UndoManager(scheduler)
    for index in range(manager.MAX_HISTORY + 1):
        manager.record_add(f"task-{index}")

    while manager.can_undo():
        manager.undo()

    assert len(scheduler.deleted) == manager.MAX_HISTORY
    assert scheduler.deleted[0] == "task-50"
    assert scheduler.deleted[-1] == "task-1"
    assert "task-0" not in scheduler.deleted


def test_failed_undo_is_logged_and_remains_available(caplog):
    manager = UndoManager(FailingScheduler())
    manager.record_add("task-1")

    with caplog.at_level("ERROR"):
        assert manager.undo() is None

    assert manager.can_undo()
    assert "Unable to undo add action" in caplog.text
