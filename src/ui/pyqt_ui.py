# pyqt_ui.py (v0.1 - DB compatible MVP)
# -------------------------------------
# Minimal compatibility update for the new DB-backed scheduler.
# Full UI overhaul will happen in a separate issue.

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

        # --- Status Bar ---
        self.statusBar().showMessage("")
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.clear_status_message)

        # --- Layout ---
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # --- Task List ---
        self.task_list = QListWidget()
        main_layout.addWidget(self.task_list)

        # Populate tasks from DB
        for entry in scheduler.list_tasks():
            date, time = self._split_due_date(entry.due_date)
            self.task_list.addItem(f"{date} {time} - {entry.title}")

        self.show_status_message("Tasks loaded")

        # --- Add Task Button ---
        add_btn = QPushButton("Add Task")
        add_btn.clicked.connect(self.open_add_dialog)
        main_layout.addWidget(add_btn)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # ---------------------------------------------------------
    # Status Bar Helpers
    # ---------------------------------------------------------

    def show_status_message(self, message, duration_ms=3000):
        self.statusBar().showMessage(message)
        self.status_timer.stop()
        self.status_timer.start(duration_ms)

    def clear_status_message(self):
        self.statusBar().clearMessage()

    # ---------------------------------------------------------
    # Add Task Dialog
    # ---------------------------------------------------------

    def open_add_dialog(self):
        dialog = AddTaskDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            date, time, text = dialog.get_values()

            if date and time and text:
                due_date = f"{date}T{time}"

                # DB-backed add
                self.scheduler.add_task(
                    title=text,
                    description=None,
                    due_date=due_date,
                )

                new_entry = self.scheduler.list_tasks()[-1]
                new_date, new_time = self._split_due_date(new_entry.due_date)

                self.task_list.addItem(
                    f"{new_date} {new_time} - {new_entry.title}"
                )

                self.show_status_message("Task added")

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _split_due_date(self, due_date: str):
        """Convert ISO 'YYYY-MM-DDTHH:MM' → ('YYYY-MM-DD', 'HH:MM')"""
        if due_date and "T" in due_date:
            return due_date.split("T", 1)
        return ("", "")


def run_pyqt_ui(scheduler):
    app = QApplication([])
    window = SchedPlusWindow(scheduler)
    window.resize(400, 500)
    window.show()
    app.exec()
