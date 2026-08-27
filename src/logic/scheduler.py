# SPDX-License-Identifier: Apache-2.0

"""
scheduler.py
-------------
SQLite-backed scheduler logic for SchedPlus.

The Scheduler class delegates all persistence to logic.storage.sqlite_storage.

UIs remain fully decoupled from storage details.
"""

import calendar
import uuid
from dataclasses import dataclass, field
from typing import List
from datetime import datetime, timezone

from .validation import validate_task


def _utc_now_iso() -> str:
    """Naive UTC timestamp matching the format stored by earlier releases."""
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date: str = ""
    time: str = ""
    text: str = ""
    createdAt: str = field(default_factory=_utc_now_iso)
    updatedAt: str = field(default_factory=_utc_now_iso)
    completed: str = ""
    completedAt: str = ""
    notes: str = ""
    priority: str = ""
    duration: str = ""
    category: str = ""
    recurrence: str = ""
    recurrenceEnd: str = ""
    reminder: str = ""


class Scheduler:
    """
    SQLite-backed scheduler.

    Responsibilities:
    - Maintain in-memory list of Task objects
    - Provide add/update/delete operations
    - Delegate persistence to sqlite_storage
    """

    def __init__(self):
        self.tasks: List[Task] = []
        from .undo_manager import UndoManager

        self.undo_manager = UndoManager(self)

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def add_task(
        self,
        date: str,
        time: str,
        text: str,
        *,
        notes: str = "",
        priority: str = "",
        duration: str = "",
        category: str = "",
        recurrence: str = "",
        recurrenceEnd: str = "",
        reminder: str = "",
    ):
        from .storage import sqlite_storage as db

        task = validate_task(
            Task(
                date=date,
                time=time,
                text=text,
                notes=notes,
                priority=priority,
                duration=duration,
                category=category,
                recurrence=recurrence,
                recurrenceEnd=recurrenceEnd,
                reminder=reminder,
            )
        )
        db.create_entry(task)
        self.tasks.append(task)
        return task

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def load_tasks(self):
        from .storage import sqlite_storage as db

        self.tasks = db.list_entries()
        return self.tasks

    def get_tasks(self) -> List[Task]:
        return self.tasks

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update_task(self, task: Task):
        from .storage import sqlite_storage as db

        validate_task(task)
        db.update_entry(task)

        # Update in-memory list
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                break

    # ---------------------------------------------------------
    # Complete / Uncomplete
    # ---------------------------------------------------------

    def complete_task(self, task_id: str):
        from dataclasses import replace
        from datetime import timedelta

        from .storage import sqlite_storage as db

        db.complete_entry(task_id)
        task = None
        for t in self.tasks:
            if t.id == task_id:
                t.completed = "true"
                t.completedAt = datetime.now(timezone.utc).isoformat()
                task = t
                break
        if task and task.recurrence and task.date:
            end = task.recurrenceEnd
            if not end or task.date <= end:
                try:
                    current = datetime.strptime(task.date, "%Y-%m-%d")
                except ValueError:
                    return
                if task.recurrence == "daily":
                    next_date = current + timedelta(days=1)
                elif task.recurrence == "weekly":
                    next_date = current + timedelta(weeks=1)
                elif task.recurrence == "monthly":
                    month = current.month + 1
                    year = current.year
                    if month > 12:
                        month = 1
                        year += 1
                    last_day = calendar.monthrange(year, month)[1]
                    next_date = current.replace(
                        year=year, month=month, day=min(current.day, last_day)
                    )
                elif task.recurrence == "yearly":
                    year = current.year + 1
                    last_day = calendar.monthrange(year, current.month)[1]
                    next_date = current.replace(
                        year=year, day=min(current.day, last_day)
                    )
                else:
                    return
                next_str = next_date.strftime("%Y-%m-%d")
                if end and next_str > end:
                    return
                new_task = replace(
                    task,
                    id=str(uuid.uuid4()),
                    date=next_str,
                    completed="",
                    completedAt="",
                    createdAt=datetime.now(timezone.utc).isoformat(),
                    updatedAt=datetime.now(timezone.utc).isoformat(),
                )
                db.create_entry(new_task)
                self.tasks.append(new_task)

    def uncomplete_task(self, task_id: str):
        from .storage import sqlite_storage as db

        db.uncomplete_entry(task_id)
        for t in self.tasks:
            if t.id == task_id:
                t.completed = ""
                t.completedAt = ""
                break

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete_task(self, task_id: str):
        from .storage import sqlite_storage as db

        db.delete_entry(task_id)
        self.tasks = [t for t in self.tasks if t.id != task_id]
