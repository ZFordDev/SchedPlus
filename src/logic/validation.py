# SPDX-License-Identifier: Apache-2.0

"""Task validation rules shared by every SchedPlus interface."""

from datetime import date as date_value
from datetime import time as time_value
from typing import Protocol, TypeVar

from .board import BOARD_STAGES


class ValidationError(ValueError):
    """Raised when a task does not meet the persistence requirements."""


class TaskLike(Protocol):
    date: str
    time: str
    text: str
    board_stage: str


TaskType = TypeVar("TaskType", bound=TaskLike)


def validate_task(task: TaskType) -> TaskType:
    """Validate and normalize a task before it is persisted."""
    if not isinstance(task.date, str):
        raise ValidationError("Date must be a valid date in YYYY-MM-DD format.")
    if not isinstance(task.time, str):
        raise ValidationError("Time must be a valid time in 24-hour HH:MM format.")
    if not isinstance(task.text, str):
        raise ValidationError("Task text cannot be empty.")

    date = task.date.strip()
    time = task.time.strip()
    text = task.text.strip()

    if not date and not time:
        # Unscheduled planning task (e.g. a Kanban card with no due date).
        if not text:
            raise ValidationError("Task text cannot be empty.")
        task.board_stage = validate_board_stage(getattr(task, "board_stage", ""))
        task.date = ""
        task.time = ""
        task.text = text
        return task

    if not date or not time:
        raise ValidationError(
            "A task must have both a date and a time, or neither (unscheduled)."
        )

    try:
        parsed_date = date_value.fromisoformat(date)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            "Date must be a valid date in YYYY-MM-DD format."
        ) from exc

    if parsed_date.isoformat() != date:
        raise ValidationError("Date must be a valid date in YYYY-MM-DD format.")

    try:
        parsed_time = time_value.fromisoformat(time)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            "Time must be a valid time in 24-hour HH:MM format."
        ) from exc

    if parsed_time.strftime("%H:%M") != time:
        raise ValidationError("Time must be a valid time in 24-hour HH:MM format.")

    if not text:
        raise ValidationError("Task text cannot be empty.")

    task.board_stage = validate_board_stage(getattr(task, "board_stage", ""))

    task.date = date
    task.time = time
    task.text = text
    return task


def validate_board_stage(value: str) -> str:
    """Normalize and validate a Kanban planning stage ('' = off the board)."""
    normalized = value.strip() if isinstance(value, str) else ""

    if normalized and normalized not in BOARD_STAGES:
        raise ValidationError(f"Board stage must be one of {', '.join(BOARD_STAGES)}.")
    return normalized
