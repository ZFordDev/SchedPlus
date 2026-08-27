# SPDX-License-Identifier: Apache-2.0

"""Task validation rules shared by every SchedPlus interface."""

from datetime import date as date_value
from datetime import time as time_value
from typing import Protocol, TypeVar


class ValidationError(ValueError):
    """Raised when a task does not meet the persistence requirements."""


class TaskLike(Protocol):
    date: str
    time: str
    text: str


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

    task.date = date
    task.time = time
    task.text = text
    return task
