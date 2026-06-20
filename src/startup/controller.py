"""
controller.py
-------------
Startup controller for SchedPlus.
"""

import sys
from .flags import determine_startup_mode
from .modes import StartupMode
from logic.storage.migration import needs_migration, run_migration


def boot():
    """
    Main entrypoint for SchedPlus startup.
    Determines startup mode and launches the correct UI.
    """

    # 0. Run migration BEFORE anything else
    if needs_migration():
        run_migration()

    # 1. Determine mode from CLI flags
    mode = determine_startup_mode(sys.argv[1:])

    # 2. If invalid flag -> stop
    if mode == StartupMode.INVALID:
        return

    # 3. If no flags -> show popup selector
    if mode == StartupMode.POPUP:
        from .selector import StartupSelector
        selector = StartupSelector()
        mode = selector.show()

        if mode is None:
            print("Startup cancelled.")
            return

    # 4. Route to correct UI
    _launch_mode(mode)


def _launch_mode(mode: StartupMode):
    """
    Launch the appropriate UI based on the resolved mode.
    Lazy imports ensure no heavy UI frameworks load unless needed.
    """

    from logic.scheduler import Scheduler
    scheduler = Scheduler()
    scheduler.load_tasks()

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
        from cli.cli_main import run_cli
        run_cli(scheduler)
        return

    else:
        print(f"[Startup] Unknown mode: {mode}")
