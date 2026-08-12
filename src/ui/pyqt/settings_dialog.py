"""Persistent preferences and their PyQt editor."""

from dataclasses import dataclass

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
    QVBoxLayout,
)

from updater.preferences import (
    UpdatePreferences,
    load_update_preferences,
    save_update_preferences,
)
from updater.config import load_build_info

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
    calendar_view: str = "month"
    first_day_of_week: str = "monday"
    workday_start: int = 7
    workday_end: int = 20


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
            calendar_view=self._choice(
                "calendar/view", {"month": "", "week": "", "day": ""}, "month"
            ),
            first_day_of_week=self._choice(
                "calendar/first_day", {"monday": "", "sunday": ""}, "monday"
            ),
            workday_start=self._hour("calendar/workday_start", 7),
            workday_end=self._hour("calendar/workday_end", 20),
        )

    def save(self, preferences: UiPreferences) -> None:
        self._settings.setValue("tasks/sort_field", preferences.sort_field)
        self._settings.setValue("tasks/sort_order", preferences.sort_order)
        self._settings.setValue("tasks/filter", preferences.task_filter)
        self._settings.setValue("ui/startup_view", preferences.startup_view)
        self._settings.setValue("calendar/view", preferences.calendar_view)
        self._settings.setValue("calendar/first_day", preferences.first_day_of_week)
        self._settings.setValue("calendar/workday_start", preferences.workday_start)
        self._settings.setValue("calendar/workday_end", preferences.workday_end)
        self._settings.sync()

    def _choice(self, key: str, choices: dict, default: str) -> str:
        value = str(self._settings.value(key, default))
        return value if value in choices else default

    def _hour(self, key: str, default: int) -> int:
        try:
            value = int(self._settings.value(key, default))
        except (TypeError, ValueError):
            return default
        return value if 0 <= value <= 23 else default


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
        self.sort_field.setCurrentIndex(
            self.sort_field.findData(preferences.sort_field)
        )

        self.sort_order = QComboBox()
        self.sort_order.addItem("Ascending", "ascending")
        self.sort_order.addItem("Descending", "descending")
        self.sort_order.setCurrentIndex(
            self.sort_order.findData(preferences.sort_order)
        )

        self.task_filter = QComboBox()
        for value, label in FILTERS.items():
            self.task_filter.addItem(label, value)
        self.task_filter.setCurrentIndex(
            self.task_filter.findData(preferences.task_filter)
        )

        self.startup_view = QComboBox()
        self.startup_view.addItem("Tasks", "tasks")
        self.startup_view.addItem("Calendar", "calendar")
        self.startup_view.setCurrentIndex(
            self.startup_view.findData(preferences.startup_view)
        )

        self.calendar_view = QComboBox()
        self.calendar_view.addItem("Month", "month")
        self.calendar_view.addItem("Week", "week")
        self.calendar_view.addItem("Day", "day")
        self.calendar_view.setCurrentIndex(
            self.calendar_view.findData(preferences.calendar_view)
        )

        self.first_day = QComboBox()
        self.first_day.addItem("Monday", "monday")
        self.first_day.addItem("Sunday", "sunday")
        self.first_day.setCurrentIndex(
            self.first_day.findData(preferences.first_day_of_week)
        )

        self.workday_start = QSpinBox()
        self.workday_start.setRange(0, 23)
        self.workday_start.setSuffix(":00")
        self.workday_start.setValue(preferences.workday_start)
        self.workday_end = QSpinBox()
        self.workday_end.setRange(0, 23)
        self.workday_end.setSuffix(":00")
        self.workday_end.setValue(preferences.workday_end)

        update_preferences = load_update_preferences()
        self.check_updates = QCheckBox("Check automatically")
        self.check_updates.setChecked(update_preferences.check_automatically)
        updates_available = load_build_info().internally_managed
        self.check_updates.setEnabled(updates_available)
        if not updates_available:
            self.check_updates.setToolTip(
                "Updates are managed by your package provider or disabled for this build."
            )

        form.addRow("Default sort", self.sort_field)
        form.addRow("Sort order", self.sort_order)
        form.addRow("Default filter", self.task_filter)
        form.addRow("Startup view", self.startup_view)
        form.addRow("Default calendar view", self.calendar_view)
        form.addRow("First day of week", self.first_day)
        form.addRow("Visible day starts", self.workday_start)
        form.addRow("Visible day ends", self.workday_end)
        form.addRow("Application updates", self.check_updates)
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
            calendar_view=self.calendar_view.currentData(),
            first_day_of_week=self.first_day.currentData(),
            workday_start=self.workday_start.value(),
            workday_end=max(self.workday_start.value(), self.workday_end.value()),
        )

    def save_update_preferences(self) -> None:
        save_update_preferences(
            UpdatePreferences(
                check_automatically=self.check_updates.isChecked(),
            )
        )
