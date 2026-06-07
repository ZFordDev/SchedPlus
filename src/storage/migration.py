"""
migration.py
------------
Handles migration from legacy JSON storage to the new SQLite database.

This module:
- Detects old JSON file
- Loads legacy tasks
- Inserts them into the DB via Repository
- Writes migration version into metadata
- Archives the old JSON file
"""

import json
import os
from typing import List

from storage.paths import get_json_path
from storage.models import Entry
from storage.repository import Repository


MIGRATION_VERSION = "1"


def needs_migration(repo: Repository) -> bool:
    """
    Returns True if migration has not been performed yet.
    """
    cursor = repo.conn.cursor()
    row = cursor.execute(
        "SELECT value FROM metadata WHERE key = 'migration_version'"
    ).fetchone()

    if row:
        return False  # already migrated

    # If JSON exists, migration is needed
    return os.path.exists(get_json_path())


def run_migration(repo: Repository) -> None:
    """
    Performs JSON → DB migration.
    """
    json_path = get_json_path()

    if not os.path.exists(json_path):
        return  # nothing to migrate

    print("[MIGRATION] Legacy JSON detected. Migrating to SQLite...")

    # Load JSON
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[MIGRATION ERROR] Failed to read JSON: {e}")
        return

    tasks = data.get("tasks", [])

    # Insert tasks into DB
    for t in tasks:
        title = t.get("text", "Untitled Task")
        date = t.get("date")
        time = t.get("time")

        # Combine date + time into ISO 8601
        due_date = None
        if date and time:
            due_date = f"{date}T{time}"

        entry = repo.create_entry(
            title=title,
            description=None,
            due_date=due_date,
        )

        # Overwrite timestamps to preserve history
        repo.update_entry(
            entry.id,
            created_at=t.get("createdAt"),
            updated_at=t.get("updatedAt"),
        )

    # Write migration version
    cursor = repo.conn.cursor()
    cursor.execute(
        "INSERT INTO metadata (key, value) VALUES ('migration_version', ?)",
        (MIGRATION_VERSION,),
    )
    repo.conn.commit()

    # Archive JSON
    backup_path = json_path + ".bak"
    try:
        os.rename(json_path, backup_path)
        print(f"[MIGRATION] JSON archived to {backup_path}")
    except Exception as e:
        print(f"[MIGRATION WARNING] Could not archive JSON: {e}")

    print("[MIGRATION] Completed successfully.")
