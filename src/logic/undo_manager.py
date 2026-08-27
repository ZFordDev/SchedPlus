"""Undo manager for task actions with a bounded history stack."""

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scheduler import Scheduler, Task


@dataclass
class UndoAction:
    action_type: str
    task_id: str
    snapshot: "Task | None" = None


class UndoManager:
    MAX_HISTORY = 50

    def __init__(self, scheduler: "Scheduler") -> None:
        self._scheduler = scheduler
        self._history: list[UndoAction] = []

    def record_add(self, task_id: str) -> None:
        self._push(UndoAction(action_type="add", task_id=task_id))

    def record_delete(self, snapshot: "Task") -> None:
        self._push(
            UndoAction(action_type="delete", task_id=snapshot.id, snapshot=snapshot)
        )

    def record_edit(self, snapshot: "Task") -> None:
        self._push(
            UndoAction(action_type="edit", task_id=snapshot.id, snapshot=snapshot)
        )

    def record_complete(self, task_id: str) -> None:
        self._push(UndoAction(action_type="complete", task_id=task_id))

    def record_uncomplete(self, task_id: str) -> None:
        self._push(UndoAction(action_type="uncomplete", task_id=task_id))

    def can_undo(self) -> bool:
        return len(self._history) > 0

    def undo(self) -> str | None:
        if not self._history:
            return None
        action = self._history.pop()
        try:
            if action.action_type == "add":
                self._scheduler.delete_task(action.task_id)
                return "Undid add"
            elif action.action_type == "delete" and action.snapshot:
                from .storage import sqlite_storage as db

                db.create_entry(action.snapshot)
                self._scheduler.tasks.append(action.snapshot)
                return "Undid delete"
            elif action.action_type == "edit" and action.snapshot:
                self._scheduler.update_task(action.snapshot)
                return "Undid edit"
            elif action.action_type == "complete":
                self._scheduler.uncomplete_task(action.task_id)
                return "Undid complete"
            elif action.action_type == "uncomplete":
                self._scheduler.complete_task(action.task_id)
                return "Undid uncomplete"
        except Exception:
            pass
        return None

    def _push(self, action: UndoAction) -> None:
        self._history.append(action)
        if len(self._history) > self.MAX_HISTORY:
            self._history.pop(0)
