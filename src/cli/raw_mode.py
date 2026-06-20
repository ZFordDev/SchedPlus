"""
raw_mode.py
-----------
Basic one-shot CLI for SchedPlus.
"""

import sys
from datetime import datetime

# ANSI colors
C_RESET = "\033[0m"
C_OK = "\033[92m"
C_WARN = "\033[91m"
C_INFO = "\033[96m"


def run_raw_mode(args, scheduler):
    if not args:
        from cli.help import show_raw_help
        return show_raw_help()

    cmd = args[0].lower()

    if cmd == "add":
        return cmd_add(scheduler)

    if cmd == "list":
        return cmd_list(scheduler)

    if cmd in ("--wipe", "--wipe!", "wipe"):
        return cmd_wipe(scheduler)

    if cmd in ("help", "--help", "-h"):
        from cli.help import show_raw_help
        return show_raw_help()

    # Unknown command → show RAW help
    from cli.help import show_raw_help
    show_raw_help()


# ---------------------------------------------------------
# ADD
# ---------------------------------------------------------

def cmd_add(scheduler):
    print(f"{C_INFO}Add new task (type 'cancel' to abort){C_RESET}")

    # Date
    while True:
        date = input("Date (DD-MM-YYYY): ").strip()
        if date.lower() == "cancel":
            print("Cancelled.")
            return

        try:
            d = datetime.strptime(date, "%d-%m-%Y")
            date_iso = d.strftime("%Y-%m-%d")
            break
        except ValueError:
            print(f"{C_WARN}Invalid date. Try again.{C_RESET}")

    # Time
    while True:
        time = input("Time (HH:MM): ").strip()
        if time.lower() == "cancel":
            print("Cancelled.")
            return

        try:
            datetime.strptime(time, "%H:%M")
            break
        except ValueError:
            print(f"{C_WARN}Invalid time. Try again.{C_RESET}")

    # Text
    text = input("Note: ").strip()
    if text.lower() == "cancel":
        print("Cancelled.")
        return

    scheduler.add_task(date=date_iso, time=time, text=text)
    print(f"{C_OK}[OK]{C_RESET} Added: {date_iso} {time} — {text}")


# ---------------------------------------------------------
# LIST
# ---------------------------------------------------------

def cmd_list(scheduler):
    tasks = scheduler.get_tasks()

    if not tasks:
        print("No tasks found.")
        return

    print(f"{C_INFO}Tasks:{C_RESET}")
    for t in tasks:
        print(f"  {t.date} {t.time} — {t.text}")


# ---------------------------------------------------------
# WIPE
# ---------------------------------------------------------

def cmd_wipe(scheduler):
    print(f"{C_WARN}WARNING: This will erase ALL tasks from the database.{C_RESET}")

    for i in range(3):
        confirm = input(f"Type 'YES' ({3-i} left): ").strip()
        if confirm != "YES":
            print("Cancelled.")
            return

    # Wipe DB
    from logic.storage.sqlite_storage import DB_FILE, init_db
    import os

    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    init_db()
    print(f"{C_OK}[OK]{C_RESET} Database wiped.")
