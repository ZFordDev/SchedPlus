"""
controller.py
-------------
Startup controller for SchedPlus.
"""

import sys

from logic.storage.sqlite_storage import StorageError, initialize_database
from updater.config import load_build_info, resolve_install_root
from updater.errors import UpdateConfigurationError, UpdateError
from updater.health import confirm_startup_health, consume_health_argument

from .flags import determine_startup_mode
from .modes import StartupMode


def boot():
    """Run the legacy flexible launcher used by ``schedplus``."""
    return boot_full()


def boot_full():
    """Run the Full edition launcher, including the interface selector."""
    return _boot()


def boot_standard():
    """Run the Standard edition directly in the PyQt interface."""
    return _boot(StartupMode.PYQT)


def boot_lite():
    """Run the Lite edition directly in the Tkinter interface."""
    return _boot(StartupMode.TK)


def boot_cli():
    """Run the CLI edition directly through command parsing."""
    return _boot(StartupMode.CLI)


def _boot(forced_mode: StartupMode | None = None):
    """Perform shared startup before launching a selected edition mode."""

    # Internal updater arguments are consumed before public CLI routing. Reaching
    # this point confirms that the replacement process and its core imports work.
    arguments, health_token = consume_health_argument(sys.argv[1:])
    if health_token:
        build_info = load_build_info()
        try:
            install_root = str(resolve_install_root(build_info))
        except UpdateConfigurationError:
            install_root = ""
        try:
            confirm_startup_health(health_token, install_root)
        except UpdateError as exc:
            print(f"SchedPlus update startup check failed: {exc}", file=sys.stderr)
            return 1

    # The full launcher retains the legacy selector and flag routing. Dedicated
    # editions deliberately skip flag routing so a frozen build starts only the
    # interface it contains.
    mode = forced_mode or determine_startup_mode(arguments)

    # 2. If invalid flag -> stop
    if mode == StartupMode.INVALID:
        return 2

    # 3. If no flags -> show popup selector
    if mode == StartupMode.POPUP:
        from .selector import StartupSelector

        selector = StartupSelector()
        selected_mode = selector.show()

        if selected_mode is None:
            print("Startup cancelled.")
            return 0
        mode = selected_mode

    # 4. Route to correct UI
    return _launch_mode(mode, arguments)


def _launch_mode(mode: StartupMode, arguments: list[str] | None = None):
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

    from logic.reminder_service import ReminderService

    reminder_service = ReminderService(scheduler)
    reminder_service.start()

    if mode == StartupMode.TK:
        try:
            from ui.tkinter_ui import run_ui
        except ImportError:
            print("Tkinter UI is not available on this system.")
            return 1

        print("[Startup] Launching Tkinter UI...")
        run_ui(scheduler, startup_notice=startup_notice)
        return 0

    elif mode == StartupMode.PYQT:
        try:
            from ui.pyqt_ui import run_pyqt_ui
        except ImportError as exc:
            print(f"PyQt UI is not available on this system: {exc}", file=sys.stderr)
            return 1

        print("[Startup] Launching PyQt UI...")
        run_pyqt_ui(scheduler, startup_notice=startup_notice)
        return 0

    elif mode == StartupMode.CLI:
        from cli.cli_main import run_cli

        if startup_notice:
            print(f"Database recovery: {startup_notice}", file=sys.stderr)
        return run_cli(scheduler, arguments)

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
        except Exception as reporter_exc:  # noqa: BLE001 - last-resort error reporter
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
        except Exception as reporter_exc:  # noqa: BLE001 - last-resort error reporter
            print(
                f"Unable to display the PyQt database error: {reporter_exc}",
                file=sys.stderr,
            )

    print(f"SchedPlus database error: {error}", file=sys.stderr)
