"""
scheduler.py (v0.4)
-------------------
Core scheduler logic for SchedPlus (v0.4).

This module provides the `Task` dataclass and the `Scheduler` class.
The `Scheduler` is responsible for in-memory task management and
exposes small wrapper methods to persist/load tasks via the storage
layer so UIs (Tkinter/PyQt) do not need to know storage paths.
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
    The Scheduler class manages a list of tasks.
    In v0.4, tasks are stored in memory and the class exposes
    simple `save_tasks`/`load_tasks` helpers that delegate to the
    storage layer. This keeps UIs decoupled from storage details.
    """

    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, date: str, time: str, text: str):
        """
        Add a new task to the scheduler.
        No validation yet — this will be added in v0.2+.
        """
        task = Task(date=date, time=time, text=text)
        self.tasks.append(task)

    def save_tasks(self, filepath: str = None):
        """
        Persist current tasks using the storage layer.

        This method performs a local import to avoid import cycles
        between `logic.storage` and `logic.scheduler`.
        """
        try:
            from . import storage as _storage

            _storage.save_tasks(self.tasks, filepath) if filepath else _storage.save_tasks(self.tasks)
        except Exception:
            # Intentionally swallow errors here; storage will log on failure.
            pass

    def load_tasks(self, filepath: str = None):
        """
        Load tasks from the storage layer into `self.tasks`.
        Returns the loaded list of tasks.
        """
        try:
            from . import storage as _storage

            self.tasks = _storage.load_tasks(filepath)
        except Exception:
            self.tasks = []

        return self.tasks

    def get_tasks(self) -> List[Task]:
        """Return the list of tasks."""
        return self.tasks
