"""
db.py
-----
SQLite engine and schema definition for SchedPlus.

This module is responsible for:
- Providing a lazy-loaded SQLite connection
- Enabling foreign key support
- Creating the database schema on first use

It is completely UI-agnostic and intended to be used by the logic layer only.
"""

import sqlite3
from typing import Optional

from storage.paths import get_db_path

_connection: Optional[sqlite3.Connection] = None


def get_connection() -> sqlite3.Connection:
    """
    Returns the global SQLite connection for SchedPlus.

    The connection is:
    - Created lazily on first use
    - Configured with foreign key support
    - Configured with sqlite3.Row for dict-like access
    - Ensures the schema exists before use
    """
    global _connection

    if _connection is None:
        db_path = get_db_path()
        _connection = sqlite3.connect(db_path)
        _connection.row_factory = sqlite3.Row

        # Enable foreign key constraints
        _connection.execute("PRAGMA foreign_keys = ON;")

        # Ensure schema exists
        _create_schema(_connection)

    return _connection


def init_db() -> None:
    """
    Initializes the database by ensuring the connection is created
    and the schema exists.

    This can be called at startup to guarantee the DB is ready.
    """
    _ = get_connection()


def _create_schema(conn: sqlite3.Connection) -> None:
    """
    Creates the database schema if it does not already exist.

    Tables:
    - entries
    - comments
    - tags
    - entry_tags (many-to-many)
    - recurrence_rules
    - metadata
    """
    cursor = conn.cursor()

    # entries: core tasks
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )

    # comments: notes attached to entries
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
        );
        """
    )

    # tags: reusable labels
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        """
    )

    # entry_tags: many-to-many between entries and tags
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS entry_tags (
            entry_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (entry_id, tag_id),
            FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE,
            FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );
        """
    )

    # recurrence_rules: future recurrence logic
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recurrence_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            rule TEXT NOT NULL,
            FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
        );
        """
    )

    # metadata: migration/versioning info
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """
    )

    conn.commit()
