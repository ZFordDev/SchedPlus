"""Scriptable command-line interface for SchedPlus."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path
from typing import TextIO

from logic.data_transfer import (
    DataTransferError,
    create_backup,
    export_tasks,
    import_tasks,
    restore_backup,
)
from logic.storage.sqlite_storage import StorageError
from logic.validation import ValidationError
from schedplus.identity import get_application_identity
from updater.errors import UpdateError

COMMANDS = {
    "add",
    "list",
    "edit",
    "complete",
    "delete",
    "backup",
    "restore",
    "export",
    "import",
    "update",
}


class CommandError(ValueError):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="schedplus",
        description="Manage SchedPlus tasks from the command line.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=get_application_identity().version_label,
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)

    add_parser = subparsers.add_parser("add", help="Create a task")
    add_parser.add_argument("text", help="Task description")
    add_parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    add_parser.add_argument(
        "--time", required=True, help="Time in 24-hour HH:MM format"
    )
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
    list_parser.add_argument(
        "--filter",
        choices=("all", "active", "completed"),
        default="all",
        help="Filter by completion status (default: all)",
    )
    list_parser.set_defaults(handler=_list_tasks)

    edit_parser = subparsers.add_parser("edit", help="Edit a task")
    edit_parser.add_argument("id", help="Full task ID or unambiguous ID prefix")
    edit_parser.add_argument("--text", help="Replacement task description")
    edit_parser.add_argument("--date", help="Replacement date in YYYY-MM-DD format")
    edit_parser.add_argument("--time", help="Replacement time in 24-hour HH:MM format")
    edit_parser.set_defaults(handler=_edit_task)

    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete or incomplete")
    complete_parser.add_argument("id", help="Full task ID or unambiguous ID prefix")
    complete_parser.set_defaults(handler=_complete_task)

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", help="Full task ID or unambiguous ID prefix")
    delete_parser.set_defaults(handler=_delete_task)

    backup_parser = subparsers.add_parser(
        "backup", help="Back up tasks and preferences"
    )
    backup_parser.add_argument("path", type=Path, help="Destination .json file")
    backup_parser.set_defaults(handler=_backup_data)

    restore_parser = subparsers.add_parser(
        "restore", help="Restore a SchedPlus backup"
    )
    restore_parser.add_argument("path", type=Path, help="Backup .json file")
    restore_parser.add_argument(
        "--yes", action="store_true", help="Confirm replacement of current data"
    )
    restore_parser.set_defaults(handler=_restore_data)

    export_parser = subparsers.add_parser(
        "export", help="Export tasks as portable JSON"
    )
    export_parser.add_argument("path", type=Path, help="Destination .json file")
    export_parser.set_defaults(handler=_export_data)

    import_parser = subparsers.add_parser(
        "import", help="Import tasks from portable JSON"
    )
    import_parser.add_argument("path", type=Path, help="Task export .json file")
    import_parser.set_defaults(handler=_import_data)

    update_parser = subparsers.add_parser("update", help="Manage application updates")
    update_commands = update_parser.add_subparsers(
        dest="update_command", metavar="ACTION", required=True
    )
    for action, help_text in (
        ("check", "Check for a compatible release"),
        ("install", "Download, verify, and install a compatible release"),
        ("status", "Show the last updater transaction"),
        ("rollback", "Restore the last-known-good managed release"),
    ):
        command = update_commands.add_parser(action, help=help_text)
        command.set_defaults(handler=_update_application)

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
    except (CommandError, DataTransferError, ValidationError) as exc:
        print(f"Error: {exc}", file=stderr)
        return 2
    except StorageError as exc:
        print(f"Database error: {exc}", file=stderr)
        return 1
    except UpdateError as exc:
        print(f"Update error: {exc}", file=stderr)
        return 1


def _add_task(options, scheduler, stdout):
    task = scheduler.add_task(options.date, options.time, options.text)
    print(f"Created {task.id}: {task.date} {task.time} — {task.text}", file=stdout)
    return 0


def _list_tasks(options, scheduler, stdout):
    tasks = list(scheduler.get_tasks())

    task_filter = getattr(options, "filter", "all")
    if task_filter == "active":
        tasks = [t for t in tasks if t.completed != "true"]
    elif task_filter == "completed":
        tasks = [t for t in tasks if t.completed == "true"]

    key_functions = {
        "date": lambda task: (task.date, task.time, task.text.casefold()),
        "time": lambda task: (task.time, task.date, task.text.casefold()),
        "text": lambda task: (task.text.casefold(), task.date, task.time),
    }
    tasks.sort(key=key_functions[options.sort], reverse=options.descending)

    if not tasks:
        print("No tasks found.", file=stdout)
        return 0

    headers = ("ID", "DATE", "TIME", "TASK", "STATUS")
    rows = [
        (task.id, task.date, task.time, task.text, "Done" if task.completed == "true" else "")
        for task in tasks
    ]
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


def _complete_task(options, scheduler, stdout):
    task = _resolve_task(scheduler, options.id)
    if task.completed == "true":
        scheduler.uncomplete_task(task.id)
        print(f"Unmarked {task.id}: {task.text}", file=stdout)
    else:
        scheduler.complete_task(task.id)
        print(f"Completed {task.id}: {task.text}", file=stdout)
    return 0


def _backup_data(options, scheduler, stdout):
    create_backup(options.path)
    print(f"Backup created: {options.path}", file=stdout)
    return 0


def _restore_data(options, scheduler, stdout):
    if not options.yes:
        raise CommandError("restore replaces current data; rerun with --yes to confirm")
    result = restore_backup(options.path)
    scheduler.load_tasks()
    print(
        f"Restored {result.restored} task(s). Previous data: {result.safety_backup}",
        file=stdout,
    )
    return 0


def _export_data(options, scheduler, stdout):
    export_tasks(options.path)
    print(f"Tasks exported: {options.path}", file=stdout)
    return 0


def _import_data(options, scheduler, stdout):
    result = import_tasks(options.path)
    scheduler.load_tasks()
    print(
        f"Imported {result.imported}; skipped {result.duplicates} duplicate(s) "
        f"and {result.conflicts} conflict(s).",
        file=stdout,
    )
    return 0


def _update_application(options, scheduler, stdout):
    from updater.checker import check_for_update
    from updater.config import load_build_info, resolve_install_root
    from updater.installer import rollback_managed_update
    from updater.service import launch_prepared_update, prepare_update
    from updater.state import UpdateState, read_state, write_state

    info = load_build_info()
    if options.update_command == "status":
        state = read_state()
        print(f"Updater status: {state.status}", file=stdout)
        if state.current_version:
            print(f"Current version: {state.current_version}", file=stdout)
        if state.target_version:
            print(f"Target version: {state.target_version}", file=stdout)
        if state.message:
            print(state.message, file=stdout)
        return 0
    if options.update_command == "check":
        try:
            result = check_for_update(info)
        except UpdateError as exc:
            write_state(
                UpdateState("failed", current_version=info.version, message=str(exc))
            )
            raise
        if result.available:
            print(f"SchedPlus {result.latest_version} is available.", file=stdout)
            message = "A compatible update is available."
        else:
            print(f"SchedPlus {info.version} is up to date.", file=stdout)
            message = "No newer compatible release was found."
        write_state(
            UpdateState(
                "available" if result.available else "up_to_date",
                current_version=info.version,
                target_version=result.latest_version,
                message=message,
            )
        )
        return 0
    if options.update_command == "rollback":
        rollback_managed_update(resolve_install_root(info))
        print("The previous SchedPlus version has been restored.", file=stdout)
        return 0

    prepared = prepare_update(info)
    launch_prepared_update(info, prepared)
    if prepared.action == "download":
        print(f"Verified update downloaded to {prepared.staged_path}", file=stdout)
    else:
        print(
            f"SchedPlus {prepared.check.latest_version} is ready. Closing to install it.",
            file=stdout,
        )
    return 0


def _resolve_task(scheduler, identifier):
    identifier = identifier.strip().lower()
    if not identifier:
        raise CommandError("task ID cannot be empty")

    exact = [task for task in scheduler.get_tasks() if task.id.lower() == identifier]
    if exact:
        return exact[0]

    matches = [
        task for task in scheduler.get_tasks() if task.id.lower().startswith(identifier)
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
