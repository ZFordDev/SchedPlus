# SPDX-License-Identifier: Apache-2.0

"""
scheduler.py
-------------
SQLite-backed scheduler logic for SchedPlus.

The Scheduler class delegates all persistence to logic.storage.sqlite_storage.

UIs remain fully decoupled from storage details.
"""

import uuid
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

from .validation import validate_task


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date: str = ""
    time: str = ""
    text: str = ""
    createdAt: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updatedAt: str = field(default_factory=lambda: datetime.utcnow().isoformat())

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

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def add_task(self, date: str, time: str, text: str):
        from .storage import sqlite_storage as db

        task = validate_task(Task(date=date, time=time, text=text))
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
    # Delete
    # ---------------------------------------------------------

    def delete_task(self, task_id: str):
        from .storage import sqlite_storage as db

        db.delete_entry(task_id)
        self.tasks = [t for t in self.tasks if t.id != task_id]
