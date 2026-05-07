"""
scheduler.py (v0.1)
-------------------
This file contains the core logic for SchedPlus.

In v0.1, the scheduler is intentionally simple:
- It stores tasks in memory
- It provides a function to add a new task
- It returns the current list of tasks

Later versions will:
- Add validation
- Add sorting
- Add editing/removal
- Move storage to a dedicated storage.py file
- Support PyQt UI
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
    In v0.1, tasks are stored in memory only.
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

    def get_tasks(self) -> List[Task]:
        """Return the list of tasks."""
        return self.tasks
