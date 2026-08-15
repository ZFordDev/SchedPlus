import json

import pytest

from cli.commands import run_command
from logic import data_transfer
from logic.scheduler import Scheduler, Task
from logic.storage import sqlite_storage
from updater import preferences as update_preferences


@pytest.fixture
def data_environment(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    database = data_dir / "tasks.db"
    data_dir.mkdir()
    monkeypatch.setattr(sqlite_storage, "prepare_database", lambda: database)
    monkeypatch.setattr(sqlite_storage, "_configure_logging", lambda _directory: None)
    monkeypatch.setattr(data_transfer, "user_data_directory", lambda: data_dir)
    monkeypatch.setattr(update_preferences, "updater_data_directory", lambda: data_dir)
    sqlite_storage.initialize_database()
    return data_dir


def _task(identifier="task-1", text="Original"):
    return Task(
        id=identifier,
        date="2026-08-15",
        time="09:30",
        text=text,
        createdAt="2026-08-15T00:00:00",
        updatedAt="2026-08-15T00:00:00",
    )


def _ui_preferences():
    return {
        "sort_field": "date",
        "sort_order": "ascending",
        "task_filter": "all",
        "startup_view": "tasks",
        "calendar_view": "week",
        "first_day_of_week": "monday",
        "workday_start": 7,
        "workday_end": 20,
    }


def test_backup_and_restore_round_trip_tasks_and_preferences(data_environment):
    sqlite_storage.create_entry(_task())
    update_preferences.save_update_preferences(
        update_preferences.UpdatePreferences(False)
    )
    backup = data_environment / "backup.json"

    data_transfer.create_backup(backup, ui_preferences=_ui_preferences())
    sqlite_storage.replace_entries([_task("replacement", "Replacement")])
    update_preferences.save_update_preferences(update_preferences.UpdatePreferences(True))

    result = data_transfer.restore_backup(backup)

    assert sqlite_storage.list_entries() == [_task()]
    assert update_preferences.load_update_preferences().check_automatically is False
    assert result.ui_preferences == _ui_preferences()
    assert result.safety_backup.exists()
    safety_document = json.loads(result.safety_backup.read_text(encoding="utf-8"))
    assert safety_document["tasks"][0]["id"] == "replacement"


def test_malformed_restore_does_not_change_data_or_create_safety_backup(
    data_environment,
):
    sqlite_storage.create_entry(_task())
    malformed = data_environment / "malformed.json"
    malformed.write_text(
        '{"format": "schedplus-backup", "format_version": 1, "tasks": []}',
        encoding="utf-8",
    )

    with pytest.raises(data_transfer.DataTransferError):
        data_transfer.restore_backup(malformed)

    assert sqlite_storage.list_entries() == [_task()]
    assert not (data_environment / "backups").exists()


def test_export_import_round_trip_and_conflict_rules(data_environment):
    original = _task()
    sqlite_storage.create_entry(original)
    export = data_environment / "tasks.json"
    data_transfer.export_tasks(export)

    first = data_transfer.import_tasks(export)
    assert first == data_transfer.ImportResult(0, 1, 0)

    document = json.loads(export.read_text(encoding="utf-8"))
    document["tasks"][0]["text"] = "Conflicting text"
    document["tasks"].append(
        {
            **document["tasks"][0],
            "id": "task-2",
            "text": "New task",
        }
    )
    export.write_text(json.dumps(document), encoding="utf-8")

    second = data_transfer.import_tasks(export)

    assert second == data_transfer.ImportResult(1, 0, 1)
    tasks = {task.id: task for task in sqlite_storage.list_entries()}
    assert tasks["task-1"].text == "Original"
    assert tasks["task-2"].text == "New task"


def test_cli_exposes_backup_restore_export_and_import(data_environment):
    sqlite_storage.create_entry(_task())
    scheduler = Scheduler()
    scheduler.load_tasks()
    backup = data_environment / "cli-backup.json"
    export = data_environment / "cli-export.json"

    assert run_command(["backup", str(backup)], scheduler) == 0
    assert run_command(["export", str(export)], scheduler) == 0
    sqlite_storage.replace_entries([])
    scheduler.load_tasks()
    assert run_command(["restore", str(backup), "--yes"], scheduler) == 0
    assert run_command(["import", str(export)], scheduler) == 0
    assert scheduler.get_tasks() == [_task()]


@pytest.mark.parametrize(
    "document",
    [
        "not json",
        '{"format":"schedplus-task-export","format_version":99,"tasks":[]}',
        '{"format":"schedplus-task-export","format_version":1,"tasks":"bad"}',
    ],
)
def test_malformed_import_is_rejected_without_changes(data_environment, document):
    sqlite_storage.create_entry(_task())
    source = data_environment / "bad.json"
    source.write_text(document, encoding="utf-8")

    with pytest.raises(data_transfer.DataTransferError):
        data_transfer.import_tasks(source)

    assert sqlite_storage.list_entries() == [_task()]
