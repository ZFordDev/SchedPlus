# pyqt_ui.py (v0.1)
# -----------------
# Teaching PyQt UI for SchedPlus.
# Mirrors the Tkinter UI but with a cleaner layout and modern widgets.

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QDialog, QDialogButtonBox, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer


class AddTaskDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Task")

        layout = QFormLayout()

        self.date_input = QLineEdit()
        self.time_input = QLineEdit()
        self.text_input = QLineEdit()

        layout.addRow("Date (YYYY-MM-DD):", self.date_input)
        layout.addRow("Time (HH:MM):", self.time_input)
        layout.addRow("Task:", self.text_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_values(self):
        return (
            self.date_input.text(),
            self.time_input.text(),
            self.text_input.text()
        )


class SchedPlusWindow(QMainWindow):
    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler

        self.setWindowTitle("SchedPlus v0.5 (PyQt)")

        # --- Status Bar (initialize first) ---
        self.statusBar().showMessage("")
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.clear_status_message)

        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # --- Task List ---
        self.task_list = QListWidget()
        main_layout.addWidget(self.task_list)

        for task in scheduler.get_tasks():
            self.task_list.addItem(
                f"{task.date} {task.time} - {task.text}"
            )

        # Display tasks loaded feedback
        self.show_status_message("Tasks loaded")

        # --- Add Task Button ---
        add_btn = QPushButton("Add Task")
        add_btn.clicked.connect(self.open_add_dialog)
        main_layout.addWidget(add_btn)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def show_status_message(self, message, duration_ms=3000):
        """Display a status message that auto-clears after the specified duration."""
        self.statusBar().showMessage(message)
        self.status_timer.stop()
        self.status_timer.start(duration_ms)

    def clear_status_message(self):
        """Clear the status bar message."""
        self.statusBar().clearMessage()

    def open_add_dialog(self):
        dialog = AddTaskDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            date, time, text = dialog.get_values()

            if date and time and text:
                self.scheduler.add_task(date, time, text)

                new_task = self.scheduler.get_tasks()[-1]
                self.task_list.addItem(
                    f"{new_task.date} {new_task.time} - {new_task.text}"
                )

                try:
                    self.scheduler.save_tasks()
                    self.show_status_message("Task saved")
                except Exception as e:
                    self.show_status_message(f"Error saving task: {str(e)}")


def run_pyqt_ui(scheduler):
    app = QApplication([])
    window = SchedPlusWindow(scheduler)
    window.resize(400, 500)
    window.show()
    app.exec()
