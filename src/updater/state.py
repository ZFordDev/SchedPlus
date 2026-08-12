# SPDX-License-Identifier: GPL-3.0-only

"""Durable update transaction state."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from logic.storage.paths import user_data_directory

from .errors import UpdateInstallError


@dataclass(frozen=True)
class UpdateState:
    status: str = "idle"
    current_version: str = ""
    target_version: str = ""
    previous_version: str = ""
    message: str = ""


def updater_data_directory() -> Path:
    return user_data_directory() / "updater"


def state_path() -> Path:
    return updater_data_directory() / "update-state.json"


def read_state() -> UpdateState:
    path = state_path()
    if not path.exists():
        return UpdateState()
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        return UpdateState(
            status=str(document.get("status", "unknown")),
            current_version=str(document.get("current_version", "")),
            target_version=str(document.get("target_version", "")),
            previous_version=str(document.get("previous_version", "")),
            message=str(document.get("message", "")),
        )
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        raise UpdateInstallError(f"Unable to read updater state: {exc}") from exc


def write_state(state: UpdateState) -> None:
    path = state_path()
    temporary = path.with_suffix(".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(
            json.dumps(asdict(state), indent=2) + "\n", encoding="utf-8"
        )
        os.replace(temporary, path)
    except OSError as exc:
        raise UpdateInstallError(f"Unable to save updater state: {exc}") from exc
