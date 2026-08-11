"""Persistent preferences and their PyQt editor."""

from dataclasses import dataclass

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QVBoxLayout


SORT_FIELDS = {
    "date": "Date",
    "time": "Time",
    "text": "Task text",
    "created": "Date created",
}
FILTERS = {
    "all": "All tasks",
    "today": "Today",
    "upcoming": "Upcoming",
}


@dataclass(frozen=True)
class UiPreferences:
    sort_field: str = "date"
    sort_order: str = "ascending"
    task_filter: str = "all"
    startup_view: str = "tasks"


class SettingsStore:
    def __init__(self):
        self._settings = QSettings("ZFordDev", "SchedPlus")

    def load(self) -> UiPreferences:
        return UiPreferences(
            sort_field=self._choice("tasks/sort_field", SORT_FIELDS, "date"),
            sort_order=self._choice(
                "tasks/sort_order", {"ascending": "", "descending": ""}, "ascending"
            ),
            task_filter=self._choice("tasks/filter", FILTERS, "all"),
            startup_view=self._choice(
                "ui/startup_view", {"tasks": "", "calendar": ""}, "tasks"
            ),
        )

    def save(self, preferences: UiPreferences) -> None:
        self._settings.setValue("tasks/sort_field", preferences.sort_field)
        self._settings.setValue("tasks/sort_order", preferences.sort_order)
        self._settings.setValue("tasks/filter", preferences.task_filter)
        self._settings.setValue("ui/startup_view", preferences.startup_view)
        self._settings.sync()

    def _choice(self, key: str, choices: dict, default: str) -> str:
        value = str(self._settings.value(key, default))
        return value if value in choices else default


class SettingsDialog(QDialog):
    def __init__(self, preferences: UiPreferences, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        form = QFormLayout()
        form.setSpacing(12)

        self.sort_field = QComboBox()
        for value, label in SORT_FIELDS.items():
            self.sort_field.addItem(label, value)
        self.sort_field.setCurrentIndex(self.sort_field.findData(preferences.sort_field))

        self.sort_order = QComboBox()
        self.sort_order.addItem("Ascending", "ascending")
        self.sort_order.addItem("Descending", "descending")
        self.sort_order.setCurrentIndex(self.sort_order.findData(preferences.sort_order))

        self.task_filter = QComboBox()
        for value, label in FILTERS.items():
            self.task_filter.addItem(label, value)
        self.task_filter.setCurrentIndex(self.task_filter.findData(preferences.task_filter))

        self.startup_view = QComboBox()
        self.startup_view.addItem("Tasks", "tasks")
        self.startup_view.addItem("Calendar", "calendar")
        self.startup_view.setCurrentIndex(
            self.startup_view.findData(preferences.startup_view)
        )

        form.addRow("Default sort", self.sort_field)
        form.addRow("Sort order", self.sort_order)
        form.addRow("Default filter", self.task_filter)
        form.addRow("Startup view", self.startup_view)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def preferences(self) -> UiPreferences:
        return UiPreferences(
            sort_field=self.sort_field.currentData(),
            sort_order=self.sort_order.currentData(),
            task_filter=self.task_filter.currentData(),
            startup_view=self.startup_view.currentData(),
        )
