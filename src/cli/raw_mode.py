"""
raw_mode.py
-----------
Basic one-shot CLI for SchedPlus.
(Might expand into a run time later)
"""

import sys
from datetime import datetime

from logic.storage.sqlite_storage import StorageError, reset_database

# ANSI colors
C_RESET = "\033[0m"
C_OK = "\033[92m"
C_WARN = "\033[91m"
C_INFO = "\033[96m"


def run_raw_mode(args, scheduler):
    # If no arguments provided, display help docs
    if not args:
        from cli.help import show_raw_help
        return show_raw_help()

    # Extract the first arg
    cmd = args[0].lower()

    # Route to the 'add' task
    if cmd == "add":
        return cmd_add(scheduler)

    # Route to the 'list' tasks display
    if cmd == "list":
        return cmd_list(scheduler)

    # Route to the 'wipe' database clearing function
    if cmd in ("--wipe", "--wipe!", "wipe"):
        return cmd_wipe(scheduler)

    # Route to help docs
    if cmd in ("help", "--help", "-h"):
        from cli.help import show_raw_help
        return show_raw_help()

    # Fallback: Unknown command triggers help display
    from cli.help import show_raw_help
    show_raw_help()


# ---------------------------------------------------------
# ADD
# ---------------------------------------------------------

def cmd_add(scheduler):
    # Prompt user to start adding a task or cancel
    print(f"{C_INFO}Add new task (type 'cancel' to abort){C_RESET}")

    # Prompt for date input with valid loop
    while True:
        date = input("Date (DD-MM-YYYY): ").strip()
        if date.lower() == "cancel":
            print("Cancelled.")
            return

        try:
            # Validate date and convert to ISO
            d = datetime.strptime(date, "%d-%m-%Y")
            date_iso = d.strftime("%Y-%m-%d")
            break
        except ValueError:
            print(f"{C_WARN}Invalid date. Try again.{C_RESET}")

    # Prompt for time input with validation loop
    # Add fuzzy logic later
    while True:
        time = input("Time (HH:MM): ").strip()
        if time.lower() == "cancel":
            print("Cancelled.")
            return

        try:
            # Validate time format (HH:MM)
            datetime.strptime(time, "%H:%M")
            break
        except ValueError:
            print(f"{C_WARN}Invalid time. Try again.{C_RESET}")

    # Prompt for task note
    text = input("Note: ").strip()
    if text.lower() == "cancel":
        print("Cancelled.")
        return

    # Add the validated task to the scheduler
    try:
        scheduler.add_task(date=date_iso, time=time, text=text)
    except StorageError as exc:
        print(f"{C_WARN}Could not add task: {exc}{C_RESET}", file=sys.stderr)
        return False
    # Confirm successful addition
    print(f"{C_OK}[OK]{C_RESET} Added: {date_iso} {time} — {text}")


# ---------------------------------------------------------
# LIST
# ---------------------------------------------------------

def cmd_list(scheduler):
    # Retrieve all tasks from the scheduler
    tasks = scheduler.get_tasks()

    # Handle case where no tasks exist
    if not tasks:
        print("No tasks found.")
        return

    # Display header and list each task
    print(f"{C_INFO}Tasks:{C_RESET}")
    for t in tasks:
        print(f"  {t.date} {t.time} — {t.text}")


# ---------------------------------------------------------
# WIPE
# ---------------------------------------------------------

def cmd_wipe(scheduler):
    # Warn user about deleting
    print(f"{C_WARN}WARNING: This will erase ALL tasks from the database.{C_RESET}")

    # Require triple confirmation ('YES') before proceeding
    # This seems safe enough for now. 
    for i in range(3):
        confirm = input(f"Type 'YES' ({3-i} left): ").strip()
        if confirm != "YES":
            print("Cancelled.")
            return

    try:
        reset_database()
    except StorageError as exc:
        print(f"{C_WARN}Could not wipe database: {exc}{C_RESET}", file=sys.stderr)
        return False
    scheduler.tasks.clear()
    # Confirm successful wipe
    print(f"{C_OK}[OK]{C_RESET} Database wiped.")
