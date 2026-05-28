# pyqt_ui.py (v0.1)
# -----------------
# Teaching PyQt UI for SchedPlus.
# Mirrors the Tkinter UI but with a cleaner layout and modern widgets.

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QDialog, QDialogButtonBox, QFormLayout
)
from PyQt6.QtCore import Qt


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


class SchedPlusWindow(QWidget):
    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler

        self.setWindowTitle("SchedPlus v0.5 (PyQt)")

        main_layout = QVBoxLayout()

        # --- Task List ---
        self.task_list = QListWidget()
        main_layout.addWidget(self.task_list)

        for task in scheduler.get_tasks():
            self.task_list.addItem(
                f"{task.date} {task.time} - {task.text}"
            )

        # --- Add Task Button ---
        add_btn = QPushButton("Add Task")
        add_btn.clicked.connect(self.open_add_dialog)
        main_layout.addWidget(add_btn)

        self.setLayout(main_layout)

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
                except Exception:
                    pass


def run_pyqt_ui(scheduler):
    app = QApplication([])
    window = SchedPlusWindow(scheduler)
    window.resize(400, 500)
    window.show()
    app.exec()
