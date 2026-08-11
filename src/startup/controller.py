"""
controller.py
-------------
Startup controller for SchedPlus.
"""

import sys
from .flags import determine_startup_mode
from .modes import StartupMode
from logic.storage.sqlite_storage import StorageError, initialize_database


def boot():
    """
    Main entrypoint for SchedPlus startup.
    Determines startup mode and launches the correct UI.
    """

    # 1. Determine mode from CLI flags
    mode = determine_startup_mode(sys.argv[1:])

    # 2. If invalid flag -> stop
    if mode == StartupMode.INVALID:
        return 2

    # 3. If no flags -> show popup selector
    if mode == StartupMode.POPUP:
        from .selector import StartupSelector
        selector = StartupSelector()
        mode = selector.show()

        if mode is None:
            print("Startup cancelled.")
            return

    # 4. Route to correct UI
    return _launch_mode(mode)


def _launch_mode(mode: StartupMode):
    """
    Launch the appropriate UI based on the resolved mode.
    Lazy imports ensure no heavy UI frameworks load unless needed.
    """

    from logic.scheduler import Scheduler
    scheduler = Scheduler()
    try:
        recovery = initialize_database()
        scheduler.load_tasks()
    except StorageError as exc:
        _report_storage_error(mode, exc)
        return 1

    startup_notice = recovery.message if recovery else None

    if mode == StartupMode.TK:
        try:
            from ui.tkinter_ui import run_ui
        except Exception:
            print("Tkinter UI is not available on this system.")
            return

        print("[Startup] Launching Tkinter UI...")
        run_ui(scheduler, startup_notice=startup_notice)
        return 0

    elif mode == StartupMode.PYQT:
        try:
            from ui.pyqt_ui import run_pyqt_ui
        except Exception:
            print("PyQt UI is not available on this system.")
            return

        print("[Startup] Launching PyQt UI...")
        run_pyqt_ui(scheduler, startup_notice=startup_notice)
        return 0

    elif mode == StartupMode.CLI:
        from cli.cli_main import run_cli
        if startup_notice:
            print(f"Database recovery: {startup_notice}", file=sys.stderr)
        return run_cli(scheduler)

    else:
        print(f"[Startup] Unknown mode: {mode}")
        return 2


def _report_storage_error(mode: StartupMode, error: StorageError) -> None:
    """Present a startup database failure through the selected interface."""
    if mode == StartupMode.TK:
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("SchedPlus database error", str(error), parent=root)
            root.destroy()
            return
        except Exception as reporter_exc:
            print(
                f"Unable to display the Tkinter database error: {reporter_exc}",
                file=sys.stderr,
            )
    elif mode == StartupMode.PYQT:
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox

            app = QApplication.instance() or QApplication([])
            QMessageBox.critical(None, "SchedPlus database error", str(error))
            app.quit()
            return
        except Exception as reporter_exc:
            print(
                f"Unable to display the PyQt database error: {reporter_exc}",
                file=sys.stderr,
            )

    print(f"SchedPlus database error: {error}", file=sys.stderr)
