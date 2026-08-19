"""Create and edit dialogs for scheduled tasks."""

from PyQt6.QtCore import QDate, QTime, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
)


class TaskDialog(QDialog):
    def __init__(self, task=None, parent=None, initial_date=None, initial_time=None):
        super().__init__(parent)
        self.setWindowTitle("Edit task" if task else "Create task")
        self.setMinimumWidth(480)
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
        self.text_input.setAccessibleName("Task description")

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setAccessibleName("Due date")

        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        self.time_input.setAccessibleName("Due time")

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Optional notes")
        self.notes_input.setClearButtonEnabled(True)
        self.notes_input.setAccessibleName("Task notes")

        self.priority_input = QComboBox()
        self.priority_input.addItems(["", "low", "medium", "high"])
        self.priority_input.setAccessibleName("Priority level")

        self.duration_input = QSpinBox()
        self.duration_input.setRange(0, 9999)
        self.duration_input.setSuffix(" min")
        self.duration_input.setSpecialValueText("—")
        self.duration_input.setToolTip("Estimated duration in minutes")
        self.duration_input.setAccessibleName("Duration in minutes")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("e.g. Work, Personal, Errands")
        self.category_input.setClearButtonEnabled(True)
        self.category_input.setAccessibleName("Task category")

        self.recurrence_input = QComboBox()
        self.recurrence_input.addItems(["", "daily", "weekly", "monthly", "yearly"])
        self.recurrence_input.setAccessibleName("Recurrence pattern")

        self.recurrence_end_input = QDateEdit()
        self.recurrence_end_input.setCalendarPopup(True)
        self.recurrence_end_input.setDisplayFormat("yyyy-MM-dd")
        self.recurrence_end_input.setDate(QDate.currentDate().addYears(1))
        self.recurrence_end_input.setSpecialValueText("No end date")
        self.recurrence_end_input.setToolTip("When recurrence stops (empty = forever)")
        self.recurrence_end_input.setAccessibleName("Recurrence end date")

        self.reminder_input = QSpinBox()
        self.reminder_input.setRange(0, 1440)
        self.reminder_input.setSuffix(" min")
        self.reminder_input.setSpecialValueText("—")
        self.reminder_input.setToolTip("Minutes before due time to notify (0 = off)")
        self.reminder_input.setAccessibleName("Reminder lead time in minutes")

        form.addRow("Task", self.text_input)
        form.addRow("Date", self.date_input)
        form.addRow("Time", self.time_input)
        form.addRow("Notes", self.notes_input)
        form.addRow("Priority", self.priority_input)
        form.addRow("Duration", self.duration_input)
        form.addRow("Category", self.category_input)
        form.addRow("Repeat", self.recurrence_input)
        form.addRow("Repeat until", self.recurrence_end_input)
        form.addRow("Remind before", self.reminder_input)
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
            self.notes_input.setText(getattr(task, "notes", "") or "")
            priority = getattr(task, "priority", "") or ""
            idx = self.priority_input.findText(priority)
            self.priority_input.setCurrentIndex(max(0, idx))
            duration_str = getattr(task, "duration", "") or ""
            try:
                self.duration_input.setValue(int(duration_str))
            except (ValueError, TypeError):
                self.duration_input.setValue(0)
            self.category_input.setText(getattr(task, "category", "") or "")
            recurrence = getattr(task, "recurrence", "") or ""
            idx = self.recurrence_input.findText(recurrence)
            self.recurrence_input.setCurrentIndex(max(0, idx))
            recurrence_end = getattr(task, "recurrenceEnd", "") or ""
            if recurrence_end:
                end_date = QDate.fromString(recurrence_end, "yyyy-MM-dd")
                if end_date.isValid():
                    self.recurrence_end_input.setDate(end_date)
            reminder = getattr(task, "reminder", "") or ""
            try:
                self.reminder_input.setValue(int(reminder))
            except (ValueError, TypeError):
                self.reminder_input.setValue(0)
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

    def get_values(self) -> tuple[str, str, str, str, str, str, str, str, str, str]:
        duration = self.duration_input.value()
        recurrence = self.recurrence_input.currentText()
        recurrence_end = ""
        if recurrence:
            recurrence_end = self.recurrence_end_input.date().toString("yyyy-MM-dd")
        reminder = self.reminder_input.value()
        return (
            self.date_input.date().toString("yyyy-MM-dd"),
            self.time_input.time().toString("HH:mm"),
            self.text_input.text(),
            self.notes_input.text(),
            self.priority_input.currentText(),
            str(duration) if duration > 0 else "",
            self.category_input.text(),
            recurrence,
            recurrence_end,
            str(reminder) if reminder > 0 else "",
        )


class AddTaskDialog(TaskDialog):
    def __init__(self, parent=None, initial_date=None, initial_time=None):
        super().__init__(
            parent=parent, initial_date=initial_date, initial_time=initial_time
        )


class EditTaskDialog(TaskDialog):
    def __init__(self, task, parent=None):
        super().__init__(task=task, parent=parent)
