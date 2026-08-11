"""Scriptable command-line interface for SchedPlus."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from typing import TextIO

from logic.storage.sqlite_storage import StorageError
from logic.validation import ValidationError


COMMANDS = {"add", "list", "edit", "delete"}


class CommandError(ValueError):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="schedplus",
        description="Manage SchedPlus tasks from the command line.",
    )
    subparsers = parser.add_subparsers(
        dest="command", metavar="COMMAND", required=True
    )

    add_parser = subparsers.add_parser("add", help="Create a task")
    add_parser.add_argument("text", help="Task description")
    add_parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    add_parser.add_argument("--time", required=True, help="Time in 24-hour HH:MM format")
    add_parser.set_defaults(handler=_add_task)

    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--sort",
        choices=("date", "time", "text"),
        default="date",
        help="Field used to sort results (default: date)",
    )
    list_parser.add_argument(
        "--descending", action="store_true", help="Reverse the sort order"
    )
    list_parser.set_defaults(handler=_list_tasks)

    edit_parser = subparsers.add_parser("edit", help="Edit a task")
    edit_parser.add_argument("id", help="Full task ID or unambiguous ID prefix")
    edit_parser.add_argument("--text", help="Replacement task description")
    edit_parser.add_argument("--date", help="Replacement date in YYYY-MM-DD format")
    edit_parser.add_argument("--time", help="Replacement time in 24-hour HH:MM format")
    edit_parser.set_defaults(handler=_edit_task)

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", help="Full task ID or unambiguous ID prefix")
    delete_parser.set_defaults(handler=_delete_task)

    return parser


def run_command(
    arguments: list[str],
    scheduler,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Parse and execute one CLI command, returning a process-style exit code."""
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = build_parser()
    options = parser.parse_args(arguments)

    try:
        return options.handler(options, scheduler, stdout)
    except (CommandError, ValidationError) as exc:
        print(f"Error: {exc}", file=stderr)
        return 2
    except StorageError as exc:
        print(f"Database error: {exc}", file=stderr)
        return 1


def _add_task(options, scheduler, stdout):
    task = scheduler.add_task(options.date, options.time, options.text)
    print(f"Created {task.id}: {task.date} {task.time} — {task.text}", file=stdout)
    return 0


def _list_tasks(options, scheduler, stdout):
    tasks = list(scheduler.get_tasks())
    key_functions = {
        "date": lambda task: (task.date, task.time, task.text.casefold()),
        "time": lambda task: (task.time, task.date, task.text.casefold()),
        "text": lambda task: (task.text.casefold(), task.date, task.time),
    }
    tasks.sort(key=key_functions[options.sort], reverse=options.descending)

    if not tasks:
        print("No tasks found.", file=stdout)
        return 0

    headers = ("ID", "DATE", "TIME", "TASK")
    rows = [(task.id, task.date, task.time, task.text) for task in tasks]
    widths = [
        max(len(headers[column]), *(len(str(row[column])) for row in rows))
        for column in range(len(headers))
    ]
    print(_format_row(headers, widths), file=stdout)
    print(_format_row(tuple("-" * width for width in widths), widths), file=stdout)
    for row in rows:
        print(_format_row(row, widths), file=stdout)
    return 0


def _edit_task(options, scheduler, stdout):
    if options.text is None and options.date is None and options.time is None:
        raise CommandError("edit requires at least one of --text, --date, or --time")

    current = _resolve_task(scheduler, options.id)
    updated = replace(
        current,
        text=options.text if options.text is not None else current.text,
        date=options.date if options.date is not None else current.date,
        time=options.time if options.time is not None else current.time,
    )
    scheduler.update_task(updated)
    print(
        f"Updated {updated.id}: {updated.date} {updated.time} — {updated.text}",
        file=stdout,
    )
    return 0


def _delete_task(options, scheduler, stdout):
    task = _resolve_task(scheduler, options.id)
    scheduler.delete_task(task.id)
    print(f"Deleted {task.id}: {task.text}", file=stdout)
    return 0


def _resolve_task(scheduler, identifier):
    identifier = identifier.strip().lower()
    if not identifier:
        raise CommandError("task ID cannot be empty")

    exact = [task for task in scheduler.get_tasks() if task.id.lower() == identifier]
    if exact:
        return exact[0]

    matches = [
        task
        for task in scheduler.get_tasks()
        if task.id.lower().startswith(identifier)
    ]
    if not matches:
        raise CommandError(f"no task matches ID '{identifier}'")
    if len(matches) > 1:
        raise CommandError(f"task ID prefix '{identifier}' is ambiguous")
    return matches[0]


def _format_row(values, widths):
    return "  ".join(
        str(value).ljust(widths[index]) for index, value in enumerate(values)
    ).rstrip()
