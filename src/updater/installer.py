# SPDX-License-Identifier: GPL-3.0-only

"""Managed-install atomic swap and last-known-good rollback."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

from .errors import UpdateInstallError
from .health import HEALTH_ARGUMENT
from .state import UpdateState, write_state

DIRECTORY_NAMES = {"current", "_old", "temp"}


def _child_path(root: Path, name: str) -> Path:
    root = root.resolve()
    child = (root / name).resolve()
    if child.parent != root or name not in DIRECTORY_NAMES:
        raise UpdateInstallError("The updater received an unsafe installation path.")
    return child


def _launch_path(current: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if not relative_path or relative.is_absolute() or ".." in relative.parts:
        raise UpdateInstallError("The packaged launch path is invalid.")
    launch = (current / relative).resolve()
    if current.resolve() not in launch.parents:
        raise UpdateInstallError("The packaged launch path escapes the installation.")
    if not launch.is_file():
        raise UpdateInstallError(f"The updated application is missing {relative_path}.")
    return launch


def wait_for_process(pid: int, *, timeout: float = 30.0) -> None:
    if pid <= 0 or pid == os.getpid():
        return
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        except PermissionError:
            pass
        time.sleep(0.1)
    raise UpdateInstallError("SchedPlus did not close in time to install the update.")


def apply_managed_update(
    root: Path,
    staged: Path,
    launch_relative_path: str,
    *,
    original_pid: int = 0,
    current_version: str = "",
    target_version: str = "",
    health_timeout: float = 20.0,
) -> None:
    """Swap a staged tree into place and restore the old tree on failed startup."""
    root = root.resolve()
    current = _child_path(root, "current")
    old = _child_path(root, "_old")
    temp = _child_path(root, "temp")
    staged = staged.resolve()
    if staged.parent != temp or not staged.is_dir():
        raise UpdateInstallError(
            "The staged update is outside the installation staging area."
        )
    if not current.is_dir():
        raise UpdateInstallError("The current SchedPlus installation is missing.")
    _launch_path(staged, launch_relative_path)
    wait_for_process(original_pid)

    write_state(
        UpdateState("installing", current_version, target_version, current_version)
    )
    if old.exists():
        shutil.rmtree(old)
    try:
        os.replace(current, old)
        os.replace(staged, current)
    except OSError as exc:
        if not current.exists() and old.exists():
            os.replace(old, current)
        raise UpdateInstallError(
            f"Unable to activate the staged update: {exc}"
        ) from exc

    token = temp / f"health-{uuid.uuid4().hex}.ok"
    try:
        launch = _launch_path(current, launch_relative_path)
        process = subprocess.Popen([str(launch), HEALTH_ARGUMENT, str(token)])
        deadline = time.monotonic() + health_timeout
        while time.monotonic() < deadline:
            if token.exists():
                write_state(
                    UpdateState(
                        "complete", target_version, target_version, current_version
                    )
                )
                token.unlink(missing_ok=True)
                return
            if process.poll() is not None:
                break
            time.sleep(0.2)
        _rollback_after_failure(current, old, process)
        write_state(
            UpdateState(
                "rolled_back",
                current_version,
                target_version,
                current_version,
                "The new release failed its startup health check.",
            )
        )
        raise UpdateInstallError(
            "The new release did not start successfully. SchedPlus restored the previous version."
        )
    except OSError as exc:
        _rollback_after_failure(current, old, None)
        raise UpdateInstallError(
            f"The updated application could not start; the previous version was restored: {exc}"
        ) from exc
    finally:
        token.unlink(missing_ok=True)


def _rollback_after_failure(
    current: Path, old: Path, process: subprocess.Popen | None
) -> None:
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    failed = current.parent / "temp" / "failed"
    if failed.exists():
        shutil.rmtree(failed)
    if current.exists():
        os.replace(current, failed)
    if old.exists():
        os.replace(old, current)


def rollback_managed_update(root: Path) -> None:
    root = root.resolve()
    current = _child_path(root, "current")
    old = _child_path(root, "_old")
    temp = _child_path(root, "temp")
    if not current.is_dir() or not old.is_dir():
        raise UpdateInstallError(
            "No previous SchedPlus version is available to restore."
        )
    failed = temp / "manual-rollback"
    temp.mkdir(parents=True, exist_ok=True)
    if failed.exists():
        shutil.rmtree(failed)
    os.replace(current, failed)
    try:
        os.replace(old, current)
    except OSError as exc:
        os.replace(failed, current)
        raise UpdateInstallError(
            f"Unable to restore the previous version: {exc}"
        ) from exc
    write_state(UpdateState(status="rolled_back", message="Manual rollback completed."))
