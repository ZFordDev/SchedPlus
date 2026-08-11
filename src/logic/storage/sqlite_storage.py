# SPDX-License-Identifier: Apache-2.0

"""SQLite persistence with structured errors and corruption recovery."""

from __future__ import annotations

import logging
import os
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, TypeVar

from ..scheduler import Task
from .paths import DatabaseMigrationError, prepare_database


LOGGER = logging.getLogger(__name__)
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS entries (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    text TEXT NOT NULL,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL
)
"""

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
    if any(getattr(handler, "_schedplus_storage", False) for handler in LOGGER.handlers):
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


def _initialize_once(path: Path) -> None:
    with closing(_connect(path)) as connection:
        with connection:
            connection.execute(SCHEMA_SQL)

        results = connection.execute("PRAGMA quick_check").fetchall()
        if results != [("ok",)]:
            details = "; ".join(str(row[0]) for row in results)
            raise _CorruptionDetected(details or "database integrity check failed")


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
            phrase in message for phrase in ("readonly", "read-only", "permission denied")
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
        with closing(_connect(path)) as connection:
            with connection:
                connection.execute(SCHEMA_SQL)
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
            INSERT INTO entries (id, date, time, text, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                task.id,
                task.date,
                task.time,
                task.text,
                task.createdAt,
                task.updatedAt,
            ),
        )
    )


def update_entry(task: Task) -> None:
    updated_at = datetime.now(timezone.utc).isoformat()
    _run(
        lambda connection: connection.execute(
            """
            UPDATE entries
            SET date = ?, time = ?, text = ?, updatedAt = ?
            WHERE id = ?
            """,
            (task.date, task.time, task.text, updated_at, task.id),
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
            "SELECT id, date, time, text, createdAt, updatedAt "
            "FROM entries WHERE id = ?",
            (task_id,),
        ).fetchone()
    )
    return _task_from_row(row) if row else None


def list_entries() -> list[Task]:
    rows = _run(
        lambda connection: connection.execute(
            """
            SELECT id, date, time, text, createdAt, updatedAt
            FROM entries
            ORDER BY date ASC, time ASC
            """
        ).fetchall()
    )
    return [_task_from_row(row) for row in rows]


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


def _task_from_row(row: tuple) -> Task:
    return Task(
        id=row[0],
        date=row[1],
        time=row[2],
        text=row[3],
        createdAt=row[4],
        updatedAt=row[5],
    )
