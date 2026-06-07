"""
scheduler.py
------------
DB-backed scheduler façade for SchedPlus.

This class used to manage JSON storage.
It now delegates all persistence to the Repository.

UI-friendly method names are preserved for compatibility:
- add_task
- update_task
- delete_task
- list_tasks
- get_task
- add_comment
- list_comments
- assign_tag
- get_tags
"""

from typing import Optional, List
from storage.repository import Repository
from storage.models import Entry, Comment, Tag


class Scheduler:
    """
    Scheduler provides a UI-friendly API for task operations.

    NEW RULE:
    - Scheduler now requires a Repository instance.
    - No JSON loading or saving.
    - No Task dataclass.
    """

    def __init__(self, repo: Repository):
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
        return self.repo.update_entry(
            entry_id=task_id,
            title=title,
            description=description,
            due_date=due_date,
            completed=completed,
        )

    def delete_task(self, task_id: int) -> None:
        self.repo.delete_entry(task_id)

    def get_task(self, task_id: int) -> Optional[Entry]:
        return self.repo.get_entry(task_id)

    def list_tasks(self) -> List[Entry]:
        return self.repo.list_entries()

    # ---------------------------------------------------------
    # Comments
    # ---------------------------------------------------------

    def add_comment(self, task_id: int, text: str) -> Comment:
        return self.repo.add_comment(task_id, text)

    def list_comments(self, task_id: int) -> List[Comment]:
        return self.repo.list_comments(task_id)

    # ---------------------------------------------------------
    # Tags
    # ---------------------------------------------------------

    def assign_tag(self, task_id: int, tag_name: str) -> Tag:
        return self.repo.assign_tag(task_id, tag_name)

    def get_tags(self) -> List[Tag]:
        return self.repo.get_tags()
