"""
pyqt_ui.py
----------
This is now just a entry point for pyqt/
"""


from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.pyqt.window import SchedPlusWindow

def run_pyqt_ui(scheduler, startup_notice=None):
    app = QApplication([])
    window = SchedPlusWindow(scheduler)
    window.show()
    if startup_notice:
        QMessageBox.warning(window, "Database recovered", startup_notice)
    app.exec()
