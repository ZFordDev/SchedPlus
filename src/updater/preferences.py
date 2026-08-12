# SPDX-License-Identifier: GPL-3.0-only

"""Cross-interface updater preferences."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass

from .errors import UpdateError
from .state import updater_data_directory


@dataclass(frozen=True)
class UpdatePreferences:
    check_automatically: bool = True


def load_update_preferences() -> UpdatePreferences:
    path = updater_data_directory() / "preferences.json"
    if not path.exists():
        return UpdatePreferences()
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return UpdatePreferences()
    return UpdatePreferences(
        check_automatically=bool(document.get("check_automatically", True)),
    )


def save_update_preferences(preferences: UpdatePreferences) -> None:
    path = updater_data_directory() / "preferences.json"
    temporary = path.with_suffix(".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(
            json.dumps(asdict(preferences), indent=2) + "\n", encoding="utf-8"
        )
        os.replace(temporary, path)
    except OSError as exc:
        raise UpdateError(f"Unable to save update preferences: {exc}") from exc
