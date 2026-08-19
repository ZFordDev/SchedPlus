# SPDX-License-Identifier: Apache-2.0

"""Ordered, transactional SQLite schema migrations."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

Migration = Callable[[sqlite3.Connection], None]


class SchemaVersionError(sqlite3.DatabaseError):
    """Raised when a database was created by a newer SchedPlus release."""


def _migration_1(connection: sqlite3.Connection) -> None:
    """Create or adopt the schema shipped by SchedPlus 0.7.3 and 0.8.0."""
    connection.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            text TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL
        )
        """)


def _migration_2(connection: sqlite3.Connection) -> None:
    """Add task completion tracking columns."""
    connection.execute("ALTER TABLE entries ADD COLUMN completed TEXT NOT NULL DEFAULT ''")
    connection.execute("ALTER TABLE entries ADD COLUMN completedAt TEXT NOT NULL DEFAULT ''")


def _migration_3(connection: sqlite3.Connection) -> None:
    """Add notes, priority, and duration columns."""
    connection.execute("ALTER TABLE entries ADD COLUMN notes TEXT NOT NULL DEFAULT ''")
    connection.execute("ALTER TABLE entries ADD COLUMN priority TEXT NOT NULL DEFAULT ''")
    connection.execute("ALTER TABLE entries ADD COLUMN duration TEXT NOT NULL DEFAULT ''")


def _migration_4(connection: sqlite3.Connection) -> None:
    """Add category column for local organization."""
    connection.execute("ALTER TABLE entries ADD COLUMN category TEXT NOT NULL DEFAULT ''")


def _migration_5(connection: sqlite3.Connection) -> None:
    """Add recurrence columns for recurring tasks."""
    connection.execute("ALTER TABLE entries ADD COLUMN recurrence TEXT NOT NULL DEFAULT ''")
    connection.execute("ALTER TABLE entries ADD COLUMN recurrenceEnd TEXT NOT NULL DEFAULT ''")


def _migration_6(connection: sqlite3.Connection) -> None:
    """Add reminder column for offline notifications."""
    connection.execute("ALTER TABLE entries ADD COLUMN reminder TEXT NOT NULL DEFAULT ''")


# Never edit or reorder a released migration. Add the next numbered callable.
MIGRATIONS: tuple[Migration, ...] = (_migration_1, _migration_2, _migration_3, _migration_4, _migration_5, _migration_6)
CURRENT_SCHEMA_VERSION = len(MIGRATIONS)


def schema_version(connection: sqlite3.Connection) -> int:
    return int(connection.execute("PRAGMA user_version").fetchone()[0])


def _available_backup_path(path: Path, old_version: int, new_version: int) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"tasks_pre_migration_v{old_version}_to_v{new_version}_{timestamp}"
    candidate = path.with_name(f"{stem}.db")
    counter = 1
    while candidate.exists():
        candidate = path.with_name(f"{stem}_{counter}.db")
        counter += 1
    return candidate


def _backup_database(
    connection: sqlite3.Connection,
    path: Path,
    old_version: int,
) -> Path:
    backup_path = _available_backup_path(path, old_version, CURRENT_SCHEMA_VERSION)
    try:
        with sqlite3.connect(backup_path) as backup_connection:
            connection.backup(backup_connection)
    except BaseException:
        try:
            backup_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return backup_path


def migrate_database(
    connection: sqlite3.Connection,
    path: Path,
    *,
    database_existed: bool,
) -> Path | None:
    """Upgrade a database in order and return its pre-migration backup path."""
    old_version = schema_version(connection)
    if old_version > CURRENT_SCHEMA_VERSION:
        raise SchemaVersionError(
            f"This database uses schema version {old_version}, but this SchedPlus "
            f"build supports only version {CURRENT_SCHEMA_VERSION}. Install a newer "
            "SchedPlus release; the database was not changed."
        )
    if old_version == CURRENT_SCHEMA_VERSION:
        return None

    backup_path = None
    if database_existed:
        backup_path = _backup_database(connection, path, old_version)

    try:
        connection.execute("BEGIN IMMEDIATE")
        for target_version in range(old_version + 1, CURRENT_SCHEMA_VERSION + 1):
            MIGRATIONS[target_version - 1](connection)
            connection.execute(f"PRAGMA user_version = {target_version}")
        connection.commit()
    except BaseException:
        connection.rollback()
        raise

    return backup_path
