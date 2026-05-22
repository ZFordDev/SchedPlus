"""
main.py (v0.4)
--------------
Entry point for SchedPlus (v0.4).

This module creates the `Scheduler`, asks it to load persisted tasks,
and launches the selected UI. UIs interact only with the scheduler API.
"""

from logic.scheduler import Scheduler
from ui.tkinter_ui import run_ui


def main():
    scheduler = Scheduler()
    # Load tasks from storage via Scheduler helper
    scheduler.load_tasks()
    run_ui(scheduler)


if __name__ == "__main__":
    main()
