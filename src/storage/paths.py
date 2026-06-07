"""
paths.py
--------
Cross-platform storage path resolver for SchedPlus.

This module defines where persistent data is stored, including:
- SQLite database file
- Legacy JSON file (for migration)
"""

import os
from appdirs import user_data_dir


APP_NAME = "SchedPlus"
APP_AUTHOR = "ZFordDev"  # optional, used on Windows


def resolve_storage_dir() -> str:
    """
    Returns the directory where SchedPlus stores all persistent data.
    Creates the directory if it does not exist.
    """
    path = user_data_dir(APP_NAME, APP_AUTHOR)

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    return path


def get_db_path() -> str:
    """
    Returns the full path to the SQLite database file.
    """
    return os.path.join(resolve_storage_dir(), "schedplus.db")


def get_json_path() -> str:
    """
    Returns the full path to the legacy JSON file (for migration).
    """
    return os.path.join(resolve_storage_dir(), "tasks.json")
