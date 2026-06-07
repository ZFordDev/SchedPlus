"""
connector.py
------------
Thin wrapper between Tkinter UI and the scheduler.

Keeps UI code clean and storage-agnostic.
"""

from .utils import build_due_date


class TkConnector:
    """
    Provides UI-friendly access to scheduler operations.

    The connector:
    - Validates UI input
    - Converts UI date/time → ISO format
    - Delegates all logic to the scheduler
    - Keeps UI code simple and logic-free
    """

    def __init__(self, scheduler):
        self.scheduler = scheduler

    # ---------------------------------------------------------
    # Read operations
    # ---------------------------------------------------------
    def list_tasks(self):
        """Return all tasks from the scheduler."""
        return self.scheduler.list_tasks()

    # ---------------------------------------------------------
    # Write operations
    # ---------------------------------------------------------
    def add_task(self, date: str, time: str, title: str) -> bool:
        """
        Validate and add a new task.

        Returns:
            bool: True if task was added, False if validation failed.
        """
        if not (date and time and title):
            return False

        due_date = build_due_date(date, time)

        self.scheduler.add_task(
            title=title,
            description=None,
            due_date=due_date,
        )

        return True
