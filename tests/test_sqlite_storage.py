import sqlite3
from pathlib import Path

import pytest

from logic.scheduler import Task
from logic.storage import sqlite_storage as storage


@pytest.fixture
def database(monkeypatch, tmp_path):
    path = tmp_path / "data" / "tasks.db"
    path.parent.mkdir()
    monkeypatch.setattr(storage, "prepare_database", lambda: path)
    monkeypatch.setattr(storage, "_configure_logging", lambda _directory: None)
    return path


def test_missing_database_is_initialized_automatically(database):
    assert not database.exists()

    assert storage.initialize_database() is None

    assert database.exists()
    assert storage.list_entries() == []


def test_corrupt_database_is_preserved_and_recreated(database):
    database.write_bytes(b"not a sqlite database")

    recovery = storage.initialize_database()

    assert recovery is not None
    assert recovery.backup_path.read_bytes() == b"not a sqlite database"
    assert recovery.backup_path.name.startswith("tasks_corrupted_")
    assert storage.list_entries() == []


def test_locked_database_has_actionable_error(database, monkeypatch):
    storage.initialize_database()
    locker = sqlite3.connect(database)
    locker.execute("BEGIN EXCLUSIVE")
    original_connect = sqlite3.connect

    def connect_quickly(path, timeout=3.0):
        return original_connect(path, timeout=0.01)

    monkeypatch.setattr(storage.sqlite3, "connect", connect_quickly)
    try:
        with pytest.raises(storage.StorageError) as caught:
            storage.create_entry(Task(text="Locked"))
    finally:
        locker.rollback()
        locker.close()

    assert caught.value.kind is storage.StorageErrorKind.LOCKED
    assert "another process" in str(caught.value)


def test_read_only_error_has_actionable_message(database, monkeypatch):
    def deny_connection(_path):
        raise sqlite3.OperationalError("attempt to write a readonly database")

    monkeypatch.setattr(storage, "_connect", deny_connection)

    with pytest.raises(storage.StorageError) as caught:
        storage.create_entry(Task(text="Read only"))

    assert caught.value.kind is storage.StorageErrorKind.READ_ONLY
    assert "permissions" in str(caught.value)


def test_integrity_error_is_translated(database):
    storage.initialize_database()
    task = Task(text="Original")
    storage.create_entry(task)

    with pytest.raises(storage.StorageError) as caught:
        storage.create_entry(task)

    assert caught.value.kind is storage.StorageErrorKind.INTEGRITY


def test_corruption_during_operation_recovers_and_requests_retry(database):
    database.write_bytes(b"not a sqlite database")

    with pytest.raises(storage.StorageError) as caught:
        storage.list_entries()

    assert caught.value.kind is storage.StorageErrorKind.RECOVERED
    assert caught.value.backup_path is not None
    assert caught.value.backup_path.exists()
    assert storage.list_entries() == []


def test_crud_round_trip(database):
    storage.initialize_database()
    task = Task(date="2026-08-12", time="09:30", text="Test recovery")

    storage.create_entry(task)
    assert storage.get_entry(task.id) == task

    task.text = "Updated"
    storage.update_entry(task)
    assert storage.get_entry(task.id).text == "Updated"

    storage.delete_entry(task.id)
    assert storage.get_entry(task.id) is None
