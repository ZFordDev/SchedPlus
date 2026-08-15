# SPDX-License-Identifier: GPL-3.0-only

"""High-level update preparation and external updater handoff."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .checker import UpdateCheckResult, check_for_update
from .config import BuildInfo, resolve_install_root, resolve_updater_executable
from .downloader import download_artifact
from .errors import UpdateConfigurationError, UpdateError
from .staging import extract_managed_zip, normalize_managed_payload


@dataclass(frozen=True)
class PreparedUpdate:
    check: UpdateCheckResult
    staged_path: Path
    action: str = "managed"


def prepare_update(info: BuildInfo) -> PreparedUpdate:
    """Discover, download, verify, and stage one compatible managed update."""
    result = check_for_update(info)
    if not result.available or result.artifact is None:
        raise UpdateError("SchedPlus is already up to date.")
    supported = {
        "managed": "managed",
        "portable": "managed",
        "managed-zip": "managed",
        "windows-installer": "installer",
        "deb": "download",
        "appimage": "download",
    }
    if info.package_format not in supported:
        raise UpdateConfigurationError(
            f"Automatic installation for {info.package_format!r} is not implemented yet."
        )
    if supported[info.package_format] == "managed":
        temp = resolve_install_root(info) / "temp"
    else:
        from .state import updater_data_directory

        temp = updater_data_directory() / "downloads"
    filename = Path(urlsplit(result.artifact.url).path).name or "update.zip"
    if supported[info.package_format] == "managed" and not filename.lower().endswith(".zip"):
        raise UpdateConfigurationError(
            "Managed updates must be delivered as ZIP archives."
        )
    archive = download_artifact(result.artifact, temp / filename)
    if supported[info.package_format] != "managed":
        return PreparedUpdate(result, archive, supported[info.package_format])
    extracted = temp / "unpacked"
    extract_managed_zip(archive, extracted)
    staged = normalize_managed_payload(
        extracted, temp / "staged", info.launch_relative_path
    )
    archive.unlink(missing_ok=True)
    return PreparedUpdate(result, staged, "managed")


def updater_command(info: BuildInfo) -> list[str]:
    if info.updater_executable:
        executable = resolve_updater_executable(info)
        if not executable.is_file():
            raise UpdateConfigurationError(
                "The packaged updater executable is missing."
            )
        return [str(executable)]
    if getattr(sys, "frozen", False):
        raise UpdateConfigurationError(
            "This build does not define an external updater."
        )
    return [sys.executable, "-m", "updater.update"]


def launch_prepared_update(
    info: BuildInfo, prepared: PreparedUpdate
) -> subprocess.Popen | None:
    """Start the independent updater; the caller must then exit normally."""
    if prepared.action == "installer":
        return subprocess.Popen([str(prepared.staged_path)], close_fds=True)
    if prepared.action == "download":
        if sys.platform == "win32":
            os.startfile(prepared.staged_path.parent)  # type: ignore[attr-defined]
            return None
        return subprocess.Popen(
            ["xdg-open", str(prepared.staged_path.parent)], close_fds=True
        )
    root = resolve_install_root(info)
    command = updater_command(info) + [
        "apply-managed",
        "--root",
        str(root),
        "--staged",
        str(prepared.staged_path),
        "--launch",
        info.launch_relative_path,
        "--pid",
        str(os.getpid()),
        "--current-version",
        info.version,
        "--target-version",
        prepared.check.latest_version,
    ]
    kwargs: dict = {"close_fds": True}
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(command, **kwargs)


def clear_staged_update(info: BuildInfo) -> None:
    root = resolve_install_root(info)
    staged = (root / "temp" / "staged").resolve()
    if staged.parent != (root / "temp").resolve():
        raise UpdateConfigurationError("The staged update path is unsafe.")
    if staged.exists():
        shutil.rmtree(staged)
