"""Validation shared by task-entry interfaces."""

from datetime import datetime


def validate_task_input(date: str, time: str, text: str) -> tuple[str, str, str]:
    """Validate and normalize values entered when creating a task."""
    date = date.strip()
    time = time.strip()
    text = text.strip()

    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Date must be a valid date in YYYY-MM-DD format.") from exc

    if parsed_date.strftime("%Y-%m-%d") != date:
        raise ValueError("Date must be a valid date in YYYY-MM-DD format.")

    try:
        parsed_time = datetime.strptime(time, "%H:%M")
    except ValueError as exc:
        raise ValueError("Time must be a valid time in 24-hour HH:MM format.") from exc

    if parsed_time.strftime("%H:%M") != time:
        raise ValueError("Time must be a valid time in 24-hour HH:MM format.")

    if not text:
        raise ValueError("Task text cannot be empty.")

    return date, time, text


def add_validated_task(scheduler, date: str, time: str, text: str):
    """Validate task input and persist it through the scheduler."""
    date, time, text = validate_task_input(date, time, text)
    return scheduler.add_task(date, time, text)
