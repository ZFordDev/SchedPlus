# SPDX-License-Identifier: Apache-2.0

"""Platform-specific paths and one-time database relocation."""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path


LOGGER = logging.getLogger(__name__)
DATABASE_NAME = "tasks.db"


class DatabaseMigrationError(RuntimeError):
    """Raised when the legacy database cannot be moved to user storage."""


def user_data_directory() -> Path:
    """Return SchedPlus's persistent per-user data directory for this package."""
    home = Path.home()

    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    else:
        # Snap changes HOME for each revision. SNAP_USER_COMMON remains stable
        # across refreshes, so it prevents an update from appearing to lose the
        # task database. Empty values intentionally fall back to normal Linux.
        snap_common = os.environ.get("SNAP_USER_COMMON", "").strip()
        if snap_common:
            return Path(snap_common) / "SchedPlus"
        base = home / ".local" / "share"

    return base / "ZFordDev" / "SchedPlus"


def database_path() -> Path:
    """Return the database path without touching the filesystem."""
    return user_data_directory() / DATABASE_NAME


def legacy_database_path() -> Path:
    """Return the database location used by SchedPlus 0.7.3 and earlier."""
    return Path(__file__).resolve().parents[2] / "data" / DATABASE_NAME


def prepare_database() -> Path:
    """Create user storage and move a legacy database there when necessary."""
    destination = database_path()
    legacy = legacy_database_path()

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if legacy.exists() and not destination.exists():
            shutil.move(str(legacy), str(destination))
            LOGGER.info("Migrated database from %s to %s", legacy, destination)
    except OSError as exc:
        raise DatabaseMigrationError(
            "SchedPlus could not move your existing database to its new user "
            f"data directory ({destination}). Your original database has not "
            f"been intentionally removed. Check directory permissions and try again."
        ) from exc

    return destination
