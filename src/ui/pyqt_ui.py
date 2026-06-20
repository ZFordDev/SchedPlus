# src/ui/pyqt_ui.py

from PyQt6.QtWidgets import QApplication
from ui.pyqt.window import SchedPlusWindow

def run_pyqt_ui(scheduler):
    app = QApplication([])
    window = SchedPlusWindow(scheduler)
    window.show()
    app.exec()
