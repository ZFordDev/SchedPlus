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
from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class Task:
    def __init__(self, date, time, text, id=None, createdAt=None, updatedAt=None):
        self.id = id or str(uuid.uuid4())
        self.date = date
        self.time = time
        self.text = text
        self.createdAt = createdAt or datetime.now()
        self.updatedAt = updatedAt or datetime.now()


    def to_dict(self):
        return {"id": self.id, 
                "date": self.date,
                "time": self.time, 
                "text": self.text, 
                "createdAt": self.createdAt, 
                "updatedAt": self.updatedAt}
    

    @classmethod
    def from_dict(cls, data):
        return cls(
        id=data["id"],
        text=data["text"],
        date=data["date"],
        time=data["time"],
        createdAt=data["createdAt"],
        updatedAt=data["updatedAt"]
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
