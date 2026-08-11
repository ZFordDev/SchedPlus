from io import StringIO

import pytest

from cli.commands import run_command
from logic.scheduler import Scheduler, Task
from logic.storage import sqlite_storage
from logic.storage.sqlite_storage import StorageError, StorageErrorKind


@pytest.fixture
def scheduler(monkeypatch):
    monkeypatch.setattr(sqlite_storage, "create_entry", lambda _task: None)
    monkeypatch.setattr(sqlite_storage, "update_entry", lambda _task: None)
    monkeypatch.setattr(sqlite_storage, "delete_entry", lambda _id: None)
    return Scheduler()


def execute(arguments, scheduler):
    stdout = StringIO()
    stderr = StringIO()
    code = run_command(arguments, scheduler, stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


def test_add_creates_validated_task(scheduler):
    code, stdout, stderr = execute(
        ["add", "Buy milk", "--date", "2026-08-03", "--time", "14:00"],
        scheduler,
    )

    assert code == 0
    assert stderr == ""
    assert "Buy milk" in stdout
    assert scheduler.tasks[0].date == "2026-08-03"


def test_add_reports_validation_errors(scheduler):
    code, stdout, stderr = execute(
        ["add", "Invalid", "--date", "2026-02-30", "--time", "14:00"],
        scheduler,
    )

    assert code == 2
    assert stdout == ""
    assert "YYYY-MM-DD" in stderr
    assert scheduler.tasks == []


def test_list_sorts_tasks_without_mutating_scheduler(scheduler):
    scheduler.tasks = [
        Task(id="b", date="2026-08-04", time="08:00", text="Alpha"),
        Task(id="a", date="2026-08-03", time="15:00", text="Zulu"),
    ]

    code, stdout, stderr = execute(["list", "--sort", "time"], scheduler)

    assert code == 0
    assert stderr == ""
    assert stdout.index("Alpha") < stdout.index("Zulu")
    assert [task.id for task in scheduler.tasks] == ["b", "a"]


def test_edit_accepts_unambiguous_id_prefix(scheduler):
    scheduler.tasks = [
        Task(
            id="abc12345-0000-0000-0000-000000000000",
            date="2026-08-03",
            time="14:00",
            text="Original",
        )
    ]

    code, stdout, stderr = execute(
        ["edit", "abc123", "--text", "Updated", "--time", "15:00"], scheduler
    )

    assert code == 0
    assert stderr == ""
    assert "Updated" in stdout
    assert scheduler.tasks[0].text == "Updated"
    assert scheduler.tasks[0].time == "15:00"


def test_edit_requires_a_changed_field(scheduler):
    scheduler.tasks = [
        Task(id="task-id", date="2026-08-03", time="14:00", text="Original")
    ]

    code, stdout, stderr = execute(["edit", "task-id"], scheduler)

    assert code == 2
    assert stdout == ""
    assert "at least one" in stderr


def test_delete_removes_task_by_id_prefix(scheduler):
    scheduler.tasks = [
        Task(
            id="def67890-0000-0000-0000-000000000000",
            date="2026-08-03",
            time="14:00",
            text="Delete me",
        )
    ]

    code, stdout, stderr = execute(["delete", "def678"], scheduler)

    assert code == 0
    assert stderr == ""
    assert "Deleted" in stdout
    assert scheduler.tasks == []


def test_ambiguous_id_prefix_is_rejected(scheduler):
    scheduler.tasks = [
        Task(id="abc-one", date="2026-08-03", time="14:00", text="One"),
        Task(id="abc-two", date="2026-08-04", time="15:00", text="Two"),
    ]

    code, stdout, stderr = execute(["delete", "abc"], scheduler)

    assert code == 2
    assert stdout == ""
    assert "ambiguous" in stderr
    assert len(scheduler.tasks) == 2


@pytest.mark.parametrize("command", [["edit", "missing", "--text", "New"], ["delete", "missing"]])
def test_missing_ids_are_reported(command, scheduler):
    code, stdout, stderr = execute(command, scheduler)

    assert code == 2
    assert stdout == ""
    assert "no task matches" in stderr


def test_database_errors_use_stderr_and_failure_exit_code():
    class FailingScheduler:
        def add_task(self, *_args):
            raise StorageError(StorageErrorKind.LOCKED, "Database is locked")

    code, stdout, stderr = execute(
        ["add", "Task", "--date", "2026-08-03", "--time", "14:00"],
        FailingScheduler(),
    )

    assert code == 1
    assert stdout == ""
    assert stderr == "Database error: Database is locked\n"
