"""
flags.py
--------
CLI flag parser for SchedPlus startup logic.

This module is UI‑agnostic and must not import any UI frameworks.
It simply interprets command‑line arguments and returns a StartupMode.
"""

from .modes import StartupMode


VALID_FLAGS = {
    "--dev": StartupMode.DEV,
    "--py": StartupMode.PYQT,
    "--tk": StartupMode.TK,
    "--raw": StartupMode.RAW,
}


def print_help():
    """Print help text for invalid or unknown flags."""
    help_text = """
SchedPlus Startup Flags:
  --dev    Use terminal selector
  --py     Launch PyQt UI
  --tk     Launch Tkinter UI
  --raw    Reserved for future RAW mode
  (no flags)  Show GUI startup selector
"""
    print(help_text.strip())


def determine_startup_mode(args) -> StartupMode:
    """
    Determine the startup mode based on CLI arguments.

    Parameters
    ----------
    args : list[str]
        Command-line arguments (excluding the script name).

    Returns
    -------
    StartupMode
        The resolved startup mode.
    """

    # No flags → show popup selector
    if not args:
        return StartupMode.POPUP

    # Only one flag is supported for now
    flag = args[0].strip().lower()

    # Valid flag
    if flag in VALID_FLAGS:
        return VALID_FLAGS[flag]

    # Invalid flag
    print_help()
    return StartupMode.INVALID
