# SPDX-License-Identifier: GPL-3.0-only

"""Post-update startup health handshakes."""

from __future__ import annotations

import os
import re
from pathlib import Path

from .errors import UpdateInstallError

HEALTH_ARGUMENT = "--update-health-token"
HEALTH_FILE_RE = re.compile(r"^health-[0-9a-f]{32}\.ok$")


def consume_health_argument(arguments: list[str]) -> tuple[list[str], str | None]:
    cleaned = list(arguments)
    try:
        index = cleaned.index(HEALTH_ARGUMENT)
    except ValueError:
        return cleaned, None
    if index + 1 >= len(cleaned):
        del cleaned[index]
        return cleaned, None
    token = cleaned[index + 1]
    del cleaned[index : index + 2]
    return cleaned, token


def confirm_startup_health(token_path: str | None, install_root: str = "") -> None:
    if not token_path:
        return
    if not install_root:
        raise UpdateInstallError(
            "A source or unmanaged build cannot confirm an update."
        )
    target = Path(token_path).resolve()
    allowed = (Path(install_root).expanduser().resolve() / "temp").resolve()
    if target.parent != allowed or not HEALTH_FILE_RE.fullmatch(target.name):
        raise UpdateInstallError("The updater health token path is invalid.")
    temporary = target.with_suffix(".tmp")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text("ok\n", encoding="utf-8")
    os.replace(temporary, target)
