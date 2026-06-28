"""
migration.py
------------
Handles migration from legacy JSON storage -> SQLite storage.
- JSON logic remains untouched
- SQLite logic remains clean
- Scheduler and UIs do not need to know about migration
"""

import os
import json
from . import sqlite_storage
from ..scheduler import Task

# Legacy JSON path (from old storage.py)
LEGACY_JSON = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "tasks.json")
)

# New SQLite DB path
SQLITE_DB = sqlite_storage.DB_FILE


# ---------------------------------------------------------
# Migration checks
# ---------------------------------------------------------

def needs_migration():
    """
    Returns True if:
    - SQLite DB does NOT exist
    - JSON file DOES exist
    """
    json_exists = os.path.exists(LEGACY_JSON)
    db_exists = os.path.exists(SQLITE_DB)

    return json_exists and not db_exists


# ---------------------------------------------------------
# Migration runner
# ---------------------------------------------------------

def run_migration():
    """
    Migrates tasks.json -> tasks.db

    Steps:
    1. Load JSON tasks
    2. Initialize SQLite DB
    3. Insert tasks
    4. Rename JSON → tasks.json.bak
    """

    print("[MIGRATION] Starting migration from JSON → SQLite")

    # 1. Load JSON tasks
    if not os.path.exists(LEGACY_JSON):
        print("[MIGRATION] No JSON file found — nothing to migrate")
        return

    try:
        with open(LEGACY_JSON, "r", encoding="utf-8") as f:
            raw = f.read()
            data = json.loads(raw)
            tasks_data = data.get("tasks", [])
    except Exception as e:
        print(f"[MIGRATION] ERROR reading JSON: {e}")
        return

    print(f"[MIGRATION] Found {len(tasks_data)} tasks in JSON")

    # Convert dicts -> Task objects
    tasks = [Task.from_dict(t) for t in tasks_data]

    # 2. Initialize SQLite DB
    sqlite_storage.init_db()

    # 3. Insert tasks into SQLite
    for task in tasks:
        sqlite_storage.create_entry(task)

    print("[MIGRATION] Inserted tasks into SQLite")

    # 4. Rename JSON -> backup
    backup_path = LEGACY_JSON + ".bak"

    try:
        os.rename(LEGACY_JSON, backup_path)
        print(f"[MIGRATION] JSON file renamed to {backup_path}")
    except Exception as e:
        print(f"[MIGRATION] WARNING: Could not rename JSON file: {e}")

    print("[MIGRATION] Migration complete")
