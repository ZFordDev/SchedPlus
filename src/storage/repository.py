"""
repository.py
-------------
UI‑agnostic repository layer for SchedPlus.

This module exposes the public CRUD API used by:
- Tkinter UI
- PyQt UI
- RAW/terminal mode (future)
- Automated scripts
- Scheduler logic

It wraps the SQLite engine and returns dataclasses defined in models.py.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from storage.db import get_connection
from storage.models import Entry, Comment, Tag, RecurrenceRule


def _now_iso() -> str:
    """Returns current time in ISO 8601 format."""
    return datetime.now().isoformat(timespec="seconds")


class Repository:
    """
    Repository provides a clean, UI‑agnostic API for all task operations.
    """

    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_connection()

    # ---------------------------------------------------------
    # Entries
    # ---------------------------------------------------------

    def create_entry(
        self,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Entry:
        now = _now_iso()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO entries (title, description, due_date, completed, created_at, updated_at)
            VALUES (?, ?, ?, 0, ?, ?)
            """,
            (title, description, due_date, now, now),
        )

        entry_id = cursor.lastrowid
        self.conn.commit()

        return self.get_entry(entry_id)

    def update_entry(
        self,
        entry_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> Optional[Entry]:
        """
        Updates only the fields provided.
        """
        entry = self.get_entry(entry_id)
        if entry is None:
            return None

        new_title = title if title is not None else entry.title
        new_desc = description if description is not None else entry.description
        new_due = due_date if due_date is not None else entry.due_date
        new_completed = int(completed) if completed is not None else int(entry.completed)

        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE entries
            SET title = ?, description = ?, due_date = ?, completed = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_title, new_desc, new_due, new_completed, _now_iso(), entry_id),
        )

        self.conn.commit()
        return self.get_entry(entry_id)

    def delete_entry(self, entry_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self.conn.commit()

    def get_entry(self, entry_id: int) -> Optional[Entry]:
        cursor = self.conn.cursor()
        row = cursor.execute(
            "SELECT * FROM entries WHERE id = ?", (entry_id,)
        ).fetchone()

        return Entry.from_row(row) if row else None

    def list_entries(self) -> List[Entry]:
        cursor = self.conn.cursor()
        rows = cursor.execute(
            "SELECT * FROM entries ORDER BY created_at DESC"
        ).fetchall()

        return [Entry.from_row(r) for r in rows]

    # ---------------------------------------------------------
    # Comments
    # ---------------------------------------------------------

    def add_comment(self, entry_id: int, text: str) -> Comment:
        now = _now_iso()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO comments (entry_id, text, created_at)
            VALUES (?, ?, ?)
            """,
            (entry_id, text, now),
        )

        comment_id = cursor.lastrowid
        self.conn.commit()

        return self.get_comment(comment_id)

    def get_comment(self, comment_id: int) -> Optional[Comment]:
        cursor = self.conn.cursor()
        row = cursor.execute(
            "SELECT * FROM comments WHERE id = ?", (comment_id,)
        ).fetchone()

        return Comment.from_row(row) if row else None

    def list_comments(self, entry_id: int) -> List[Comment]:
        cursor = self.conn.cursor()
        rows = cursor.execute(
            """
            SELECT * FROM comments
            WHERE entry_id = ?
            ORDER BY created_at ASC
            """,
            (entry_id,),
        ).fetchall()

        return [Comment.from_row(r) for r in rows]

    # ---------------------------------------------------------
    # Tags
    # ---------------------------------------------------------

    def get_tags(self) -> List[Tag]:
        cursor = self.conn.cursor()
        rows = cursor.execute("SELECT * FROM tags ORDER BY name ASC").fetchall()
        return [Tag.from_row(r) for r in rows]

    def assign_tag(self, entry_id: int, tag_name: str) -> Tag:
        """
        Ensures tag exists, then links it to the entry.
        """
        cursor = self.conn.cursor()

        # 1. Ensure tag exists
        row = cursor.execute(
            "SELECT * FROM tags WHERE name = ?", (tag_name,)
        ).fetchone()

        if row:
            tag = Tag.from_row(row)
        else:
            cursor.execute(
                "INSERT INTO tags (name) VALUES (?)",
                (tag_name,),
            )
            tag = Tag(id=cursor.lastrowid, name=tag_name)

        # 2. Link entry <-> tag
        cursor.execute(
            """
            INSERT OR IGNORE INTO entry_tags (entry_id, tag_id)
            VALUES (?, ?)
            """,
            (entry_id, tag.id),
        )

        self.conn.commit()
        return tag
