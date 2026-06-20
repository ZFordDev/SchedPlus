"""
scheduler.py (v0.6)
-------------------
SQLite-backed scheduler logic for SchedPlus.

The Scheduler class now delegates all persistence to
logic.storage.sqlite_storage instead of the legacy JSON storage.

UIs remain fully decoupled from storage details.
"""

import uuid
from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date: str = ""
    time: str = ""
    text: str = ""
    createdAt: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updatedAt: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "time": self.time,
            "text": self.text,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            date=data.get("date", ""),
            time=data.get("time", ""),
            text=data.get("text", ""),
            createdAt=data.get("createdAt", datetime.utcnow().isoformat()),
            updatedAt=data.get("updatedAt", datetime.utcnow().isoformat()),
        )


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

        task = Task(date=date, time=time, text=text)
        db.create_entry(task)
        self.tasks.append(task)

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
