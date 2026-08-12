import sys

sys.path.insert(0, SPECPATH)

from common import build


app = build(
    edition="SchedPlusCli",
    entry_point="cli_launcher.py",
    excludes=["PyQt6", "tkinter", "tkinter.ttk", "tkcalendar"],
    console=True,
)
