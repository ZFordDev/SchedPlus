import sys

sys.path.insert(0, SPECPATH)

from common import build


app = build(
    edition="SchedPlusStandard",
    entry_point="standard.py",
    excludes=["tkinter", "tkinter.ttk", "tkcalendar"],
    console=False,
    hiddenimports=[
        "ui.pyqt_ui",
        "ui.pyqt.window",
        "ui.pyqt.add_dialog",
        "ui.pyqt.calendar_view",
        "ui.pyqt.settings_dialog",
        "ui.pyqt.task_list",
        "ui.pyqt.theme",
    ],
)
