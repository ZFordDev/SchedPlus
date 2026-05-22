import json
import os
from .scheduler import Task  # import the dataclass Task

SCHEMA_VERSION = 1

# Absolute / robust path relative to this file
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "tasks.json")
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)



def save_tasks(tasks, filepath=DATA_FILE):
    """
    Save list of Task objects to JSON file
    """
    data = {
        "version": SCHEMA_VERSION,
        "tasks": [t.to_dict() for t in tasks],  # convert each Task → dict
    }

    try:
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to save tasks: {e}")


def load_tasks(filepath=DATA_FILE):
    """
    Load JSON file → return list of Task objects
    """
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        tasks_data = data.get("tasks", [])
        return [Task.from_dict(t) for t in tasks_data]  # convert dict → Task
    except Exception as e:
        print(f"[ERROR] Failed to load tasks: {e}")
        return []