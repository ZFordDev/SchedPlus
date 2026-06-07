"""
scheduler.py
------------
The Scheduler is now a thin façade over the Repository.

IMPORTANT:
- All JSON save/load logic has been removed.
- All persistence is now handled by the Repository (SQLite).
- The old Task dataclass is deprecated and replaced by Entry.
- Method names are preserved for UI compatibility.

This module does NOT:
- Read or write JSON
- Manage file paths
- Perform schema logic
- Talk directly to SQLite

It ONLY delegates to the Repository.
"""

from typing import Optional, List
from storage.repository import Repository
from storage.models import Entry, Comment, Tag


class Scheduler:
    """
    Scheduler provides a UI-friendly API for task operations.

    NOTE:
    - This class used to manage JSON storage.
    - It now depends entirely on the Repository for persistence.
    - All CRUD operations are DB-backed.
    """

    def __init__(self, repo: Repository):
        # NEW RULE: Scheduler requires a Repository instance.
        self.repo = repo

    # ---------------------------------------------------------
    # Task CRUD (Entry CRUD)
    # ---------------------------------------------------------

    def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Entry:
        """
        Create a new task (Entry) in the database.
        """
        return self.repo.create_entry(
            title=title,
            description=description,
            due_date=due_date,
        )

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> Optional[Entry]:
        """
        Update an existing task.
        Only fields provided will be updated.
        """
        return self.repo.update_entry(
            entry_id=task_id,
            title=title,
            description=description,
            due_date=due_date,
            completed=completed,
        )

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task from the database.
        """
        self.repo.delete_entry(task_id)

    def get_task(self, task_id: int) -> Optional[Entry]:
        """
        Retrieve a single task by ID.
        """
        return self.repo.get_entry(task_id)

    def list_tasks(self) -> List[Entry]:
        """
        Return all tasks, newest first.
        """
        return self.repo.list_entries()

    # ---------------------------------------------------------
    # Comments
    # ---------------------------------------------------------

    def add_comment(self, task_id: int, text: str) -> Comment:
        """
        Add a comment to a task.
        """
        return self.repo.add_comment(task_id, text)

    def list_comments(self, task_id: int) -> List[Comment]:
        """
        List all comments for a task.
        """
        return self.repo.list_comments(task_id)

    # ---------------------------------------------------------
    # Tags
    # ---------------------------------------------------------

    def assign_tag(self, task_id: int, tag_name: str) -> Tag:
        """
        Assign a tag to a task.
        Creates the tag if it does not exist.
        """
        return self.repo.assign_tag(task_id, tag_name)

    def get_tags(self) -> List[Tag]:
        """
        Return all tags in the system.
        """
        return self.repo.get_tags()
