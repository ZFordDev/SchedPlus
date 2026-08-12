# SPDX-License-Identifier: GPL-3.0-only

"""Safe extraction of managed-install update archives."""

from __future__ import annotations

import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath

from .errors import UpdateInstallError, UpdateVerificationError


def extract_managed_zip(archive: Path, staging_directory: Path) -> Path:
    """Extract a ZIP without symlinks, traversal, or absolute paths."""
    archive = archive.resolve()
    staging_directory = staging_directory.resolve()
    if staging_directory.exists():
        shutil.rmtree(staging_directory)
    staging_directory.mkdir(parents=True)
    try:
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                relative = PurePosixPath(member.filename)
                if (
                    relative.is_absolute()
                    or ".." in relative.parts
                    or not relative.parts
                    or relative.parts[0] in {"", "."}
                ):
                    raise UpdateVerificationError(
                        "The update archive contains an unsafe file path."
                    )
                mode = member.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise UpdateVerificationError(
                        "The update archive contains an unsupported symbolic link."
                    )
                target = staging_directory.joinpath(*relative.parts)
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(member) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
                if mode & stat.S_IXUSR:
                    target.chmod(target.stat().st_mode | stat.S_IXUSR)
    except (OSError, zipfile.BadZipFile) as exc:
        raise UpdateInstallError(
            f"Unable to stage the downloaded update: {exc}"
        ) from exc
    return staging_directory
