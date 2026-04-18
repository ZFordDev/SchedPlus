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

from dataclasses import dataclass
from typing import List


@dataclass
class Task:
    """A simple data structure to hold a scheduled task."""
    date: str   # e.g. "2026-04-19"
    time: str   # e.g. "06:45"
    text: str   # e.g. "Deliver paperwork"


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
