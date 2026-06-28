import json
import os
from .scheduler import Task

SCHEMA_VERSION = 2

DATA_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "tasks.json")
)
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)


def save_tasks(tasks, filepath=DATA_FILE):
    print("\n[SAVE] ----------------------------------------")
    print("[SAVE] Path:", filepath)
    print("[SAVE] tasks list:", tasks)
    print("[SAVE] tasks count:", len(tasks))
    print("[SAVE] file exists before save:", os.path.exists(filepath))

    # Prevent wiping existing file with empty list
    if not tasks and os.path.exists(filepath):
        print("[SAVE] ABORTED — empty task list would overwrite existing file")
        return

    data = {
        "version": SCHEMA_VERSION,
        "tasks": [t.to_dict() for t in tasks],
    }

    try:
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("[SAVE] SUCCESS — wrote JSON")
    except Exception as e:
        print(f"[SAVE] ERROR:", e)


def load_tasks(filepath=DATA_FILE):
    print("\n[LOAD] ----------------------------------------")
    print("[LOAD] Path:", filepath)
    print("[LOAD] file exists:", os.path.exists(filepath))

    if not os.path.exists(filepath):
        print("[LOAD] No file — returning empty list")
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
            print("[LOAD] Raw file contents:", raw)

            data = json.loads(raw)

        tasks_data = data.get("tasks", [])
        print("[LOAD] Parsed tasks:", tasks_data)
        print("[LOAD] Count:", len(tasks_data))

        tasks = [Task.from_dict(t) for t in tasks_data]
        print("[LOAD] Converted to Task objects:", tasks)

        return tasks

    except Exception as e:
        print(f"[LOAD] ERROR:", e)
        return []
