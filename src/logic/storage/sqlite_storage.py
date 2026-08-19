# SPDX-License-Identifier: Apache-2.0

"""SQLite persistence with structured errors and corruption recovery."""

from __future__ import annotations

import logging
import os
import sqlite3
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TypeVar

from ..scheduler import Task
from .migrations import SchemaVersionError, migrate_database
from .paths import DatabaseMigrationError, prepare_database

LOGGER = logging.getLogger(__name__)
T = TypeVar("T")


class StorageErrorKind(Enum):
    LOCKED = "locked"
    READ_ONLY = "read_only"
    CORRUPT = "corrupt"
    RECOVERED = "recovered"
    INTEGRITY = "integrity"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class StorageError(RuntimeError):
    """A database failure safe to present at an application boundary."""

    def __init__(
        self,
        kind: StorageErrorKind,
        message: str,
        *,
        backup_path: Path | None = None,
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.backup_path = backup_path


@dataclass(frozen=True)
class RecoveryInfo:
    backup_path: Path

    @property
    def message(self) -> str:
        return (
            "SchedPlus found a damaged database and created a fresh one. "
            f"The original was preserved at:\n{self.backup_path}"
        )


class _CorruptionDetected(sqlite3.DatabaseError):
    pass


def _configure_logging(data_directory: Path) -> None:
    """Configure one rotating storage log without duplicating handlers."""
    if any(
        getattr(handler, "_schedplus_storage", False) for handler in LOGGER.handlers
    ):
        return

    try:
        handler = RotatingFileHandler(
            data_directory / "schedplus.log",
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
            delay=False,
        )
    except OSError:
        LOGGER.exception("Unable to configure the SchedPlus storage log")
        return

    handler._schedplus_storage = True
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = True


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=3.0)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _quick_check(connection: sqlite3.Connection) -> None:
    results = connection.execute("PRAGMA quick_check").fetchall()
    if results != [("ok",)]:
        details = "; ".join(str(row[0]) for row in results)
        raise _CorruptionDetected(details or "database integrity check failed")


def _initialize_once(path: Path) -> None:
    existed = path.exists()
    with closing(_connect(path)) as connection:
        _quick_check(connection)
        backup = migrate_database(connection, path, database_existed=existed)
        if backup is not None:
            LOGGER.info("Created pre-migration database backup at %s", backup)
        _quick_check(connection)


def _sqlite_code(exc: sqlite3.Error) -> int | None:
    code = getattr(exc, "sqlite_errorcode", None)
    return code & 0xFF if isinstance(code, int) else None


def _is_corruption(exc: sqlite3.Error) -> bool:
    return isinstance(exc, _CorruptionDetected) or _sqlite_code(exc) in {
        sqlite3.SQLITE_CORRUPT,
        sqlite3.SQLITE_NOTADB,
    }


def _storage_error(exc: BaseException) -> StorageError:
    if isinstance(exc, DatabaseMigrationError):
        return StorageError(StorageErrorKind.UNAVAILABLE, str(exc))

    if isinstance(exc, SchemaVersionError):
        return StorageError(StorageErrorKind.UNAVAILABLE, str(exc))

    if isinstance(exc, OSError):
        return StorageError(
            StorageErrorKind.UNAVAILABLE,
            "SchedPlus cannot access its data directory. Check the directory "
            "permissions and available disk space, then try again.",
        )

    if isinstance(exc, sqlite3.IntegrityError):
        return StorageError(
            StorageErrorKind.INTEGRITY,
            "SchedPlus could not save this task because it conflicts with existing data.",
        )

    if isinstance(exc, sqlite3.Error):
        code = _sqlite_code(exc)
        message = str(exc).lower()
        if code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in message:
            return StorageError(
                StorageErrorKind.LOCKED,
                "The SchedPlus database is busy or locked by another process. "
                "Close other SchedPlus windows, wait a moment, and try again.",
            )
        if code in {sqlite3.SQLITE_READONLY, sqlite3.SQLITE_PERM} or any(
            phrase in message
            for phrase in ("readonly", "read-only", "permission denied")
        ):
            return StorageError(
                StorageErrorKind.READ_ONLY,
                "SchedPlus cannot write to its data directory. Check the directory "
                "permissions and available disk space, then try again.",
            )
        if code in {sqlite3.SQLITE_CANTOPEN, sqlite3.SQLITE_IOERR, sqlite3.SQLITE_FULL}:
            return StorageError(
                StorageErrorKind.UNAVAILABLE,
                "SchedPlus cannot access its database. Check the data directory "
                "permissions and available disk space, then try again.",
            )

    return StorageError(
        StorageErrorKind.UNKNOWN,
        "SchedPlus encountered an unexpected database error. See schedplus.log "
        "in the application data directory for details.",
    )


def _backup_path(path: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = path.with_name(f"tasks_corrupted_{timestamp}.db")
    counter = 1
    while candidate.exists():
        candidate = path.with_name(f"tasks_corrupted_{timestamp}_{counter}.db")
        counter += 1
    return candidate


def _recover_corrupt_database(path: Path) -> RecoveryInfo:
    backup = _backup_path(path)
    LOGGER.exception("Database corruption detected; preserving %s as %s", path, backup)

    try:
        if not path.exists():
            raise OSError("the damaged database disappeared before recovery")
        os.replace(path, backup)
        for suffix in ("-wal", "-shm"):
            sidecar = Path(f"{path}{suffix}")
            if sidecar.exists():
                os.replace(sidecar, Path(f"{backup}{suffix}"))
        _initialize_once(path)
    except (OSError, sqlite3.Error) as recovery_exc:
        LOGGER.exception("Automatic database recovery failed")
        raise StorageError(
            StorageErrorKind.CORRUPT,
            "The SchedPlus database is damaged and automatic recovery failed. "
            f"Your data may be preserved at {backup}. Check schedplus.log for details.",
            backup_path=backup if backup.exists() else None,
        ) from recovery_exc

    LOGGER.info("Database recovery completed; backup stored at %s", backup)
    return RecoveryInfo(backup)


def initialize_database() -> RecoveryInfo | None:
    """Create and verify the database, recovering confirmed corruption once."""
    try:
        path = prepare_database()
        _configure_logging(path.parent)
        existed = path.exists()
        _initialize_once(path)
        if not existed:
            LOGGER.info("Created a new database at %s", path)
        return None
    except (DatabaseMigrationError, OSError) as exc:
        LOGGER.exception("Unable to prepare the database")
        raise _storage_error(exc) from exc
    except sqlite3.Error as exc:
        if _is_corruption(exc):
            return _recover_corrupt_database(path)
        LOGGER.exception("Unable to initialize the database")
        raise _storage_error(exc) from exc


def _run(operation: Callable[[sqlite3.Connection], T]) -> T:
    """Run a complete database operation with rollback, cleanup, and translation."""
    try:
        path = prepare_database()
        _configure_logging(path.parent)
        existed = path.exists()
        with closing(_connect(path)) as connection:
            _quick_check(connection)
            backup = migrate_database(connection, path, database_existed=existed)
            if backup is not None:
                LOGGER.info("Created pre-migration database backup at %s", backup)
            with connection:
                return operation(connection)
    except (DatabaseMigrationError, OSError) as exc:
        LOGGER.exception("Database path operation failed")
        raise _storage_error(exc) from exc
    except sqlite3.Error as exc:
        if _is_corruption(exc):
            recovery = _recover_corrupt_database(path)
            raise StorageError(
                StorageErrorKind.RECOVERED,
                recovery.message,
                backup_path=recovery.backup_path,
            ) from exc
        LOGGER.exception("SQLite operation failed")
        raise _storage_error(exc) from exc


def init_db() -> RecoveryInfo | None:
    """Backward-compatible alias for database initialization."""
    return initialize_database()


def create_entry(task: Task) -> None:
    _run(
        lambda connection: connection.execute(
            """
            INSERT INTO entries (id, date, time, text, createdAt, updatedAt, completed, completedAt, notes, priority, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.id,
                task.date,
                task.time,
                task.text,
                task.createdAt,
                task.updatedAt,
                task.completed,
                task.completedAt,
                task.notes,
                task.priority,
                task.duration,
            ),
        )
    )


def update_entry(task: Task) -> None:
    updated_at = datetime.now(timezone.utc).isoformat()
    _run(
        lambda connection: connection.execute(
            """
            UPDATE entries
            SET date = ?, time = ?, text = ?, updatedAt = ?, completed = ?, completedAt = ?,
                notes = ?, priority = ?, duration = ?
            WHERE id = ?
            """,
            (task.date, task.time, task.text, updated_at, task.completed, task.completedAt,
             task.notes, task.priority, task.duration, task.id),
        )
    )
    task.updatedAt = updated_at


def delete_entry(task_id: str) -> None:
    _run(
        lambda connection: connection.execute(
            "DELETE FROM entries WHERE id = ?", (task_id,)
        )
    )


def get_entry(task_id: str) -> Task | None:
    row = _run(
        lambda connection: connection.execute(
            "SELECT id, date, time, text, createdAt, updatedAt, completed, completedAt, notes, priority, duration "
            "FROM entries WHERE id = ?",
            (task_id,),
        ).fetchone()
    )
    return _task_from_row(row) if row else None


def list_entries() -> list[Task]:
    rows = _run(lambda connection: connection.execute("""
            SELECT id, date, time, text, createdAt, updatedAt, completed, completedAt, notes, priority, duration
            FROM entries
            ORDER BY date ASC, time ASC
            """).fetchall())
    return [_task_from_row(row) for row in rows]


def replace_entries(tasks: list[Task]) -> None:
    """Replace all tasks atomically after callers have validated the payload."""
    def replace(connection: sqlite3.Connection) -> None:
        connection.execute("DELETE FROM entries")
        connection.executemany(
            "INSERT INTO entries (id, date, time, text, createdAt, updatedAt, completed, completedAt, notes, priority, duration) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [_task_values(task) for task in tasks],
        )

    _run(replace)


def import_entries(tasks: list[Task]) -> tuple[int, int, int]:
    """Insert new IDs; return imported, duplicate, and conflicting counts."""
    def merge(connection: sqlite3.Connection) -> tuple[int, int, int]:
        imported = duplicates = conflicts = 0
        for task in tasks:
            row = connection.execute(
                "SELECT id, date, time, text, createdAt, updatedAt, completed, completedAt, notes, priority, duration "
                "FROM entries WHERE id = ?",
                (task.id,),
            ).fetchone()
            if row is None:
                connection.execute(
                    "INSERT INTO entries (id, date, time, text, createdAt, updatedAt, completed, completedAt, notes, priority, duration) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    _task_values(task),
                )
                imported += 1
            elif row == _task_values(task):
                duplicates += 1
            else:
                conflicts += 1
        return imported, duplicates, conflicts

    return _run(merge)


def reset_database() -> None:
    """Remove all task data and create a clean database."""
    try:
        path = prepare_database()
        _configure_logging(path.parent)
        for candidate in (path, Path(f"{path}-wal"), Path(f"{path}-shm")):
            if candidate.exists():
                candidate.unlink()
        _initialize_once(path)
        LOGGER.info("Database reset completed")
    except (DatabaseMigrationError, OSError, sqlite3.Error) as exc:
        LOGGER.exception("Unable to reset the database")
        raise _storage_error(exc) from exc


def complete_entry(task_id: str) -> None:
    from datetime import datetime, timezone
    completed_at = datetime.now(timezone.utc).isoformat()
    _run(
        lambda connection: connection.execute(
            "UPDATE entries SET completed = 'true', completedAt = ? WHERE id = ?",
            (completed_at, task_id),
        )
    )


def uncomplete_entry(task_id: str) -> None:
    _run(
        lambda connection: connection.execute(
            "UPDATE entries SET completed = '', completedAt = '' WHERE id = ?",
            (task_id,),
        )
    )


def list_completed_entries() -> list[Task]:
    rows = _run(lambda connection: connection.execute("""
            SELECT id, date, time, text, createdAt, updatedAt, completed, completedAt
            FROM entries
            WHERE completed = 'true'
            ORDER BY completedAt DESC
            """).fetchall())
    return [_task_from_row(row) for row in rows]


def _task_from_row(row: tuple) -> Task:
    return Task(
        id=row[0],
        date=row[1],
        time=row[2],
        text=row[3],
        createdAt=row[4],
        updatedAt=row[5],
        completed=row[6] if len(row) > 6 else "",
        completedAt=row[7] if len(row) > 7 else "",
        notes=row[8] if len(row) > 8 else "",
        priority=row[9] if len(row) > 9 else "",
        duration=row[10] if len(row) > 10 else "",
    )


def _task_values(task: Task) -> tuple[str, str, str, str, str, str, str, str, str, str, str]:
    return (task.id, task.date, task.time, task.text, task.createdAt, task.updatedAt,
            task.completed, task.completedAt, task.notes, task.priority, task.duration)
