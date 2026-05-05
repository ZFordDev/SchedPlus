"""
main.py (v0.1)
--------------
This file is the entry point for SchedPlus.

Right now it:
- Creates a Scheduler instance
- Launches the Tkinter UI

Later versions will:
- Allow switching between Tkinter and PyQt
- Handle configuration
- Manage storage loading/saving
"""

from logic.scheduler import Scheduler
from ui.tkinter_ui import run_ui
from logic.storage import load_tasks


def main():
    scheduler = Scheduler()
    # Load tasks from JSON into Scheduler
    scheduler.tasks = load_tasks()
    print("Tasks loaded at startup:", scheduler.get_tasks())
    run_ui(scheduler)
    


if __name__ == "__main__":
    main()
