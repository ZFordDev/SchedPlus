import sqlite3

import pytest

from logic.storage import migrations
from logic.storage import sqlite_storage as storage

LEGACY_SCHEMA = """
CREATE TABLE entries (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    text TEXT NOT NULL,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL
)
"""


@pytest.fixture
def database(monkeypatch, tmp_path):
    path = tmp_path / "data" / "tasks.db"
    path.parent.mkdir()
    monkeypatch.setattr(storage, "prepare_database", lambda: path)
    monkeypatch.setattr(storage, "_configure_logging", lambda _directory: None)
    return path


def _create_legacy_database(path, release):
    with sqlite3.connect(path) as connection:
        connection.execute(LEGACY_SCHEMA)
        connection.execute(
            "INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?)",
            (
                f"from-{release}",
                "2026-08-15",
                "09:30",
                f"Created by SchedPlus {release}",
                "2026-08-15T00:00:00",
                "2026-08-15T00:00:00",
            ),
        )


@pytest.mark.parametrize("release", ["0.7.3", "0.8.0"])
def test_released_database_is_upgraded_with_backup(database, release):
    _create_legacy_database(database, release)

    assert storage.initialize_database() is None

    with sqlite3.connect(database) as connection:
        assert (
            migrations.schema_version(connection) == migrations.CURRENT_SCHEMA_VERSION
        )
        assert connection.execute("SELECT id, text FROM entries").fetchone() == (
            f"from-{release}",
            f"Created by SchedPlus {release}",
        )

    backups = list(
        database.parent.glob(
            f"tasks_pre_migration_v0_to_v{migrations.CURRENT_SCHEMA_VERSION}_*.db"
        )
    )
    assert len(backups) == 1
    with sqlite3.connect(backups[0]) as connection:
        assert migrations.schema_version(connection) == 0
        assert connection.execute("SELECT id FROM entries").fetchone() == (
            f"from-{release}",
        )


def test_new_database_is_versioned_without_empty_backup(database):
    storage.initialize_database()

    with sqlite3.connect(database) as connection:
        assert (
            migrations.schema_version(connection) == migrations.CURRENT_SCHEMA_VERSION
        )
    assert list(database.parent.glob("tasks_pre_migration_*.db")) == []


def test_migrations_run_in_order(database, monkeypatch):
    _create_legacy_database(database, "0.8.0")
    applied = []

    def migration_2(connection):
        applied.append(2)
        connection.execute("CREATE TABLE migration_two (id INTEGER)")

    def migration_3(connection):
        applied.append(3)
        connection.execute("CREATE TABLE migration_three (id INTEGER)")

    monkeypatch.setattr(
        migrations, "MIGRATIONS", (migrations.MIGRATIONS[0], migration_2, migration_3)
    )
    monkeypatch.setattr(migrations, "CURRENT_SCHEMA_VERSION", 3)

    storage.initialize_database()

    assert applied == [2, 3]
    with sqlite3.connect(database) as connection:
        assert migrations.schema_version(connection) == 3


def test_failed_migration_rolls_back_and_preserves_backup(database, monkeypatch):
    _create_legacy_database(database, "0.8.0")

    def failing_migration(connection):
        connection.execute("CREATE TABLE must_be_rolled_back (id INTEGER)")
        raise sqlite3.OperationalError("injected migration failure")

    monkeypatch.setattr(
        migrations, "MIGRATIONS", (migrations.MIGRATIONS[0], failing_migration)
    )
    monkeypatch.setattr(migrations, "CURRENT_SCHEMA_VERSION", 2)

    with pytest.raises(storage.StorageError):
        storage.initialize_database()

    with sqlite3.connect(database) as connection:
        assert migrations.schema_version(connection) == 0
        assert connection.execute("SELECT id FROM entries").fetchone() == (
            "from-0.8.0",
        )
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name = 'must_be_rolled_back'"
            ).fetchone()
            is None
        )

    backups = list(database.parent.glob("tasks_pre_migration_v0_to_v2_*.db"))
    assert len(backups) == 1
    with sqlite3.connect(backups[0]) as connection:
        assert connection.execute("SELECT id FROM entries").fetchone() == (
            "from-0.8.0",
        )


def test_newer_schema_is_refused_without_modification_or_backup(database):
    _create_legacy_database(database, "future")
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA user_version = 99")

    with pytest.raises(storage.StorageError) as caught:
        storage.initialize_database()

    assert caught.value.kind is storage.StorageErrorKind.UNAVAILABLE
    assert "schema version 99" in str(caught.value)
    with sqlite3.connect(database) as connection:
        assert migrations.schema_version(connection) == 99
        assert connection.execute("SELECT id FROM entries").fetchone() == (
            "from-future",
        )
    assert list(database.parent.glob("tasks_pre_migration_*.db")) == []
