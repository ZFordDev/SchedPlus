"""Create and edit dialogs for scheduled tasks."""

from PyQt6.QtCore import QDate, QTime, Qt
from PyQt6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTimeEdit,
    QVBoxLayout,
)


class TaskDialog(QDialog):
    def __init__(self, task=None, parent=None, initial_date=None, initial_time=None):
        super().__init__(parent)
        self.setWindowTitle("Edit task" if task else "Create task")
        self.setMinimumWidth(440)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        heading = QLabel("Edit task" if task else "Create a new task")
        heading.setObjectName("DialogHeading")
        layout.addWidget(heading)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("What needs to be done?")
        self.text_input.setClearButtonEnabled(True)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")

        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")

        form.addRow("Task", self.text_input)
        form.addRow("Date", self.date_input)
        form.addRow("Time", self.time_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if task:
            self.text_input.setText(task.text)
            self.date_input.setDate(QDate.fromString(task.date, "yyyy-MM-dd"))
            self.time_input.setTime(QTime.fromString(task.time, "HH:mm"))
        else:
            selected_date = QDate.fromString(initial_date or "", "yyyy-MM-dd")
            selected_time = QTime.fromString(initial_time or "", "HH:mm")
            self.date_input.setDate(
                selected_date if selected_date.isValid() else QDate.currentDate()
            )
            self.time_input.setTime(
                selected_time if selected_time.isValid() else QTime.currentTime()
            )

        self.text_input.setFocus()

    def get_values(self) -> tuple[str, str, str]:
        return (
            self.date_input.date().toString("yyyy-MM-dd"),
            self.time_input.time().toString("HH:mm"),
            self.text_input.text(),
        )


class AddTaskDialog(TaskDialog):
    def __init__(self, parent=None, initial_date=None, initial_time=None):
        super().__init__(
            parent=parent, initial_date=initial_date, initial_time=initial_time
        )


class EditTaskDialog(TaskDialog):
    def __init__(self, task, parent=None):
        super().__init__(task=task, parent=parent)
