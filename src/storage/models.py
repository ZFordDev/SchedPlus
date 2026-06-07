"""
models.py
---------
Dataclasses representing core SchedPlus entities.

These are UI-agnostic and used by the repository and logic layer.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Entry:
    id: int
    title: str
    description: Optional[str]
    due_date: Optional[str]  # ISO 8601 string or None
    completed: bool
    created_at: str          # ISO 8601
    updated_at: str          # ISO 8601

    @classmethod
    def from_row(cls, row) -> "Entry":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            due_date=row["due_date"],
            completed=bool(row["completed"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class Comment:
    id: int
    entry_id: int
    text: str
    created_at: str  # ISO 8601

    @classmethod
    def from_row(cls, row) -> "Comment":
        return cls(
            id=row["id"],
            entry_id=row["entry_id"],
            text=row["text"],
            created_at=row["created_at"],
        )


@dataclass
class Tag:
    id: int
    name: str

    @classmethod
    def from_row(cls, row) -> "Tag":
        return cls(
            id=row["id"],
            name=row["name"],
        )


@dataclass
class RecurrenceRule:
    id: int
    entry_id: int
    rule: str

    @classmethod
    def from_row(cls, row) -> "RecurrenceRule":
        return cls(
            id=row["id"],
            entry_id=row["entry_id"],
            rule=row["rule"],
        )
