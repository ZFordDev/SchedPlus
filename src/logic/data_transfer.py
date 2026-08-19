# SPDX-License-Identifier: Apache-2.0

"""Offline, versioned backup, restore, export, and import operations."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from schedplus.identity import get_application_identity
from updater.preferences import (
    UpdatePreferences,
    load_update_preferences,
    save_update_preferences,
)

from .scheduler import Task
from .storage import sqlite_storage
from .storage.paths import user_data_directory
from .validation import ValidationError, validate_task

BACKUP_FORMAT = "schedplus-backup"
EXPORT_FORMAT = "schedplus-task-export"
FORMAT_VERSION = 1
UI_PREFERENCES_NAME = "ui-preferences.json"
UI_KEYS = {
    "sort_field",
    "sort_order",
    "task_filter",
    "startup_view",
    "calendar_view",
    "first_day_of_week",
    "workday_start",
    "workday_end",
}


class DataTransferError(ValueError):
    """A malformed or inaccessible local transfer file."""


@dataclass(frozen=True)
class ImportResult:
    imported: int
    duplicates: int
    conflicts: int


@dataclass(frozen=True)
class RestoreResult:
    restored: int
    safety_backup: Path
    ui_preferences: dict[str, Any] | None


def create_backup(path: Path, *, ui_preferences: dict[str, Any] | None = None) -> None:
    if ui_preferences is None:
        ui_preferences = load_ui_preferences()
    elif ui_preferences is not None:
        ui_preferences = _validate_ui_preferences(ui_preferences)
    document = _document(BACKUP_FORMAT, sqlite_storage.list_entries())
    document["preferences"] = {
        "updates": asdict(load_update_preferences()),
        "ui": ui_preferences,
    }
    _write_json(path, document)


def restore_backup(
    path: Path, *, current_ui_preferences: dict[str, Any] | None = None
) -> RestoreResult:
    document = _read_document(path, BACKUP_FORMAT)
    tasks = _parse_tasks(document.get("tasks"))
    preferences = document.get("preferences")
    if not isinstance(preferences, dict):
        raise DataTransferError("Backup preferences must be an object.")
    updates = preferences.get("updates")
    if not isinstance(updates, dict) or not isinstance(
        updates.get("check_automatically"), bool
    ):
        raise DataTransferError("Backup update preferences are invalid.")
    ui_preferences = preferences.get("ui")
    if ui_preferences is not None:
        ui_preferences = _validate_ui_preferences(ui_preferences)

    safety_backup = _safety_backup_path()
    create_backup(safety_backup, ui_preferences=current_ui_preferences)
    sqlite_storage.replace_entries(tasks)
    save_update_preferences(UpdatePreferences(updates["check_automatically"]))
    if ui_preferences is not None:
        save_ui_preferences(ui_preferences)
    return RestoreResult(len(tasks), safety_backup, ui_preferences)


def export_tasks(path: Path) -> None:
    _write_json(path, _document(EXPORT_FORMAT, sqlite_storage.list_entries()))


def import_tasks(path: Path) -> ImportResult:
    document = _read_document(path, EXPORT_FORMAT)
    tasks = _parse_tasks(document.get("tasks"))
    imported, duplicates, conflicts = sqlite_storage.import_entries(tasks)
    return ImportResult(imported, duplicates, conflicts)


def load_ui_preferences() -> dict[str, Any] | None:
    path = user_data_directory() / UI_PREFERENCES_NAME
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return _validate_ui_preferences(value)
    except (OSError, UnicodeError, json.JSONDecodeError, DataTransferError):
        return None


def save_ui_preferences(preferences: dict[str, Any]) -> None:
    _write_json(
        user_data_directory() / UI_PREFERENCES_NAME,
        _validate_ui_preferences(preferences),
    )


def _document(format_name: str, tasks: list[Task]) -> dict[str, Any]:
    return {
        "format": format_name,
        "format_version": FORMAT_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "application_version": get_application_identity().version,
        "tasks": [asdict(task) for task in tasks],
    }


def _read_document(path: Path, expected_format: str) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DataTransferError(f"Unable to read a valid JSON file: {exc}") from exc
    if not isinstance(document, dict):
        raise DataTransferError("The file must contain a JSON object.")
    if document.get("format") != expected_format:
        raise DataTransferError(f"This is not a {expected_format} file.")
    if document.get("format_version") != FORMAT_VERSION:
        raise DataTransferError(
            f"Unsupported format version {document.get('format_version')!r}."
        )
    return document


def _parse_tasks(value: object) -> list[Task]:
    if not isinstance(value, list):
        raise DataTransferError("The tasks field must be a list.")
    tasks = []
    seen_ids: set[str] = set()
    required = {"id", "date", "time", "text", "createdAt", "updatedAt"}
    optional = {"completed", "completedAt", "notes", "priority", "duration"}
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise DataTransferError(f"Task {index} has invalid fields.")
        if not required.issubset(item):
            raise DataTransferError(f"Task {index} has invalid fields.")
        unknown = set(item) - required - optional
        if unknown:
            raise DataTransferError(f"Task {index} has unknown fields: {unknown}")
        if not all(isinstance(item[key], str) for key in required):
            raise DataTransferError(f"Task {index} fields must be strings.")
        if not item["id"].strip() or item["id"] in seen_ids:
            raise DataTransferError(f"Task {index} has an empty or duplicate ID.")
        try:
            datetime.fromisoformat(item["createdAt"])
            datetime.fromisoformat(item["updatedAt"])
            task_kwargs = {key: item[key] for key in required}
            for opt in optional:
                task_kwargs[opt] = item.get(opt, "")
            task = validate_task(Task(**task_kwargs))
        except (TypeError, ValueError, ValidationError) as exc:
            raise DataTransferError(f"Task {index} is invalid: {exc}") from exc
        seen_ids.add(task.id)
        tasks.append(task)
    return tasks


def _validate_ui_preferences(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != UI_KEYS:
        raise DataTransferError("Backup UI preferences have invalid fields.")
    choices = {
        "sort_field": {"date", "time", "text", "status", "created"},
        "sort_order": {"ascending", "descending"},
        "task_filter": {"all", "active", "completed", "today", "upcoming"},
        "startup_view": {"tasks", "calendar"},
        "calendar_view": {"month", "week", "day"},
        "first_day_of_week": {"monday", "sunday"},
    }
    if any(value[key] not in allowed for key, allowed in choices.items()):
        raise DataTransferError("Backup UI preferences contain unsupported values.")
    start, end = value["workday_start"], value["workday_end"]
    if (
        not isinstance(start, int)
        or isinstance(start, bool)
        or not isinstance(end, int)
        or isinstance(end, bool)
        or not 0 <= start <= end <= 23
    ):
        raise DataTransferError("Backup workday preferences are invalid.")
    return dict(value)


def _write_json(path: Path, document: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    except OSError as exc:
        raise DataTransferError(f"Unable to write {path}: {exc}") from exc


def _safety_backup_path() -> Path:
    directory = user_data_directory() / "backups"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = directory / f"SchedPlus-before-restore-{timestamp}.json"
    counter = 1
    while candidate.exists():
        candidate = directory / f"SchedPlus-before-restore-{timestamp}-{counter}.json"
        counter += 1
    return candidate
