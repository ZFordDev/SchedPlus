import sys

sys.path.insert(0, SPECPATH)

from common import build


app = build(
    edition="SchedPlusStandard",
    entry_point="standard.py",
    excludes=["tkinter", "tkinter.ttk", "tkcalendar"],
    console=False,
)
