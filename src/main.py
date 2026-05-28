"""
main.py (v0.4)
--------------
Entry point for SchedPlus (v0.4).

This module creates the `Scheduler`, asks it to load persisted tasks,
and launches the selected UI. UIs interact only with the scheduler API.
"""

from logic.scheduler import Scheduler
from ui.tkinter_ui import run_ui
from ui.pyqt_ui import run_pyqt_ui


def choose_ui():
    prompt = "Choose UI: [1] Tkinter, [2] PyQt (experimental)\nSelection [1]: "
    choice = input(prompt).strip()
    return choice == "2"


def main():
    scheduler = Scheduler()
    # Load tasks from storage via Scheduler helper
    scheduler.load_tasks()

    if choose_ui():
        run_pyqt_ui(scheduler)
    else:
        run_ui(scheduler)


if __name__ == "__main__":
    main()
