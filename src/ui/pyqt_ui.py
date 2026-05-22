"""
pyqt_ui.py (v0.1)
------------------
Minimal PyQt prototype window for SchedPlus.

This module provides a tiny, standalone PyQt window used to
establish the PyQt import paths, event loop, and a safe place
to build the production UI in v0.5.

Notes:
- This file intentionally does not integrate with the Scheduler.
- Keep it minimal: a window title and a short label.
"""


def run_ui():
    """Launch a minimal PyQt window.

    Raises ImportError if PyQt5 is not installed.
    """
    try:
        from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
    except Exception as e:
        raise ImportError("PyQt5 is required to run the PyQt UI. Install with `pip install PyQt5`.") from e

    app = QApplication.instance() or QApplication([])

    win = QWidget()
    win.setWindowTitle("SchedPlus (PyQt Prototype)")

    layout = QVBoxLayout()
    layout.addWidget(QLabel("PyQt Prototype UI — work in progress"))
    win.setLayout(layout)

    win.resize(400, 120)
    win.show()

    # Start the Qt event loop. If this function is called from an
    # existing QApplication, this will simply continue the loop.
    app.exec_()


def run_pyqt_ui():
    """Placeholder stub for the experimental PyQt UI path."""
    print("PyQt UI is experimental and not available in this release.")
    print("Please choose Tkinter to use the stable UI.")


if __name__ == "__main__":
    run_ui()
