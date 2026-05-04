import json
import os

SCHEMA_VERSION = 1


def save_tasks(tasks, filepath):
    data = {
        "version": SCHEMA_VERSION,
        "tasks": tasks,
    }

    try:
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to save tasks: {e}")


def load_tasks(filepath):
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Task file must contain a JSON object at the root.")

        tasks = data.get("tasks", [])
        if not isinstance(tasks, list):
            raise ValueError("The 'tasks' field must be a list.")

        return tasks
    except Exception as e:
        print(f"[ERROR] Failed to load tasks: {e}")
        return []
