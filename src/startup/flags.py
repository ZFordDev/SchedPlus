"""
flags.py
--------
CLI flag parser for SchedPlus startup logic.

This module is UI-agnostic and must not import any UI frameworks.
It simply interprets command-line arguments and returns a StartupMode.
"""

from .modes import StartupMode
from cli.help import show_startup_help


VALID_FLAGS = {
    "--py": StartupMode.PYQT,
    "--tk": StartupMode.TK,
    "--raw": StartupMode.RAW,
}


def determine_startup_mode(args) -> StartupMode:
    """
    Determine the startup mode based on CLI arguments.
    """

    # No args -> popup selector
    if not args:
        return StartupMode.POPUP

    flag = args[0].strip().lower()

    # Valid flag
    if flag in VALID_FLAGS:
        return VALID_FLAGS[flag]

    # Invalid flag -> show help
    show_startup_help()
    return StartupMode.INVALID
