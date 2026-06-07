"""
controller.py
-------------
Startup controller for SchedPlus.

This module orchestrates the boot process:
- Reads CLI flags
- Shows popup selector if needed
- Launches the correct UI
- Handles missing dependencies gracefully

NEW (DB-backed):
- Initializes SQLite
- Runs JSON → DB migration if needed
- Injects Repository into Scheduler

This file must not contain UI logic or storage logic.
"""

import sys
from .flags import determine_startup_mode
from .modes import StartupMode


def boot():
    """
    Main entrypoint for SchedPlus startup.
    Determines startup mode and launches the correct UI.
    """

    # 1. Determine mode from CLI flags
    mode = determine_startup_mode(sys.argv[1:])

    # 2. If invalid flag → stop
    if mode == StartupMode.INVALID:
        return

    # 3. If no flags → show popup selector
    if mode == StartupMode.POPUP:
        from .selector import StartupSelector
        selector = StartupSelector()
        mode = selector.show()

        # User closed popup
        if mode is None:
            print("Startup cancelled.")
            return

    # 4. Route to correct UI
    _launch_mode(mode)


def _launch_mode(mode: StartupMode):
    """
    Launch the appropriate UI based on the resolved mode.
    Lazy imports ensure no heavy UI frameworks load unless needed.

    NEW:
    - DB initialization
    - Migration
    - Repository + Scheduler wiring
    """

    # ---------------------------------------------------------
    # NEW: Initialize DB + Repository + Migration
    # ---------------------------------------------------------
    from storage.db import init_db
    from storage.repository import Repository
    from storage.migration import needs_migration, run_migration
    from logic.scheduler import Scheduler

    # 1. Ensure DB + schema exist
    init_db()

    # 2. Create repository
    repo = Repository()

    # 3. Run migration if needed
    if needs_migration(repo):
        run_migration(repo)

    # 4. Create DB-backed scheduler
    scheduler = Scheduler(repo)

    # ---------------------------------------------------------
    # OLD UI routing (unchanged)
    # ---------------------------------------------------------

    if mode == StartupMode.TK:
        try:
            from ui.tkinter_ui import run_ui
        except Exception:
            print("Tkinter UI is not available on this system.")
            return

        print("[Startup] Launching Tkinter UI...")
        run_ui(scheduler)

    elif mode == StartupMode.PYQT:
        try:
            from ui.pyqt_ui import run_pyqt_ui
        except Exception:
            print("PyQt UI is not available on this system.")
            return

        print("[Startup] Launching PyQt UI...")
        run_pyqt_ui(scheduler)

    elif mode == StartupMode.DEV:
        print("[Startup] Developer mode not implemented yet.")
        return

    elif mode == StartupMode.RAW:
        print("[Startup] RAW mode not implemented yet.")
        return

    else:
        print(f"[Startup] Unknown mode: {mode}")
