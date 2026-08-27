"""Persistent preferences and their PyQt editor."""

import platform
from dataclasses import asdict, dataclass

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from logic.data_transfer import load_ui_preferences, save_ui_preferences
from logic.storage.paths import database_path
from updater.config import load_build_info
from updater.preferences import (
    UpdatePreferences,
    load_update_preferences,
    save_update_preferences,
)

SORT_FIELDS = {
    "date": "Date",
    "time": "Time",
    "text": "Task text",
    "status": "Status",
    "created": "Date created",
}
FILTERS = {
    "all": "All tasks",
    "active": "Active",
    "completed": "Completed",
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
    date_format: str = "yyyy-MM-dd"
    time_format: str = "HH:mm"
    show_week_numbers: bool = True


DATE_FORMATS = {
    "yyyy-MM-dd": "YYYY-MM-DD (ISO)",
    "MM/dd/yyyy": "MM/DD/YYYY (US)",
    "dd/MM/yyyy": "DD/MM/YYYY (EU)",
    "dd.MM.yyyy": "DD.MM.YYYY (DE)",
}
TIME_FORMATS = {
    "HH:mm": "24-hour (HH:mm)",
    "h:mm AP": "12-hour (h:mm AM/PM)",
}


class SettingsStore:
    def __init__(self):
        self._settings = QSettings("ZFordDev", "SchedPlus")

    def load(self) -> UiPreferences:
        portable = load_ui_preferences()
        if portable is not None:
            try:
                return UiPreferences(**portable)
            except TypeError:
                pass
        preferences = UiPreferences(
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
            date_format=self._choice("formats/date", DATE_FORMATS, "yyyy-MM-dd"),
            time_format=self._choice("formats/time", TIME_FORMATS, "HH:mm"),
            show_week_numbers=self._bool("formats/week_numbers", True),
        )
        return preferences

    def save(self, preferences: UiPreferences) -> None:
        save_ui_preferences(asdict(preferences))
        self._settings.setValue("tasks/sort_field", preferences.sort_field)
        self._settings.setValue("tasks/sort_order", preferences.sort_order)
        self._settings.setValue("tasks/filter", preferences.task_filter)
        self._settings.setValue("ui/startup_view", preferences.startup_view)
        self._settings.setValue("calendar/view", preferences.calendar_view)
        self._settings.setValue("calendar/first_day", preferences.first_day_of_week)
        self._settings.setValue("calendar/workday_start", preferences.workday_start)
        self._settings.setValue("calendar/workday_end", preferences.workday_end)
        self._settings.setValue("formats/date", preferences.date_format)
        self._settings.setValue("formats/time", preferences.time_format)
        self._settings.setValue("formats/week_numbers", preferences.show_week_numbers)
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

    def _bool(self, key: str, default: bool) -> bool:
        value = self._settings.value(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes")


class SettingsDialog(QDialog):
    def __init__(self, preferences: UiPreferences, scheduler=None, parent=None):
        super().__init__(parent)
        self._scheduler = scheduler
        self.setWindowTitle("Settings")
        self.setMinimumSize(480, 440)
        self.resize(560, 620)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        tabs = QTabWidget()
        tabs.addTab(
            self._scrollable_tab(self._build_general_tab(preferences)), "General"
        )
        tabs.addTab(self._scrollable_tab(self._build_data_tab()), "Data")
        tabs.addTab(self._scrollable_tab(self._build_about_tab()), "About")
        layout.addWidget(tabs)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _scrollable_tab(self, content: QWidget) -> QScrollArea:
        """Keep every tab usable on small screens or enlarged system fonts."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(content)
        return scroll

    def _build_general_tab(self, preferences: UiPreferences) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setSpacing(10)

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

        self.updates_managed_internally = load_build_info().internally_managed
        update_preferences = load_update_preferences()
        self.check_updates = QCheckBox("Check automatically")
        if self.updates_managed_internally:
            self.check_updates.setChecked(update_preferences.check_automatically)
        else:
            # Store-managed builds (Snap, MSIX) cannot self-update; presenting a
            # ticked checkbox would misrepresent who applies updates.
            self.check_updates.setChecked(False)
            self.check_updates.setEnabled(False)
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

        self.date_format = QComboBox()
        for value, label in DATE_FORMATS.items():
            self.date_format.addItem(label, value)
        self.date_format.setCurrentIndex(
            self.date_format.findData(preferences.date_format)
        )

        self.time_format = QComboBox()
        for value, label in TIME_FORMATS.items():
            self.time_format.addItem(label, value)
        self.time_format.setCurrentIndex(
            self.time_format.findData(preferences.time_format)
        )

        self.show_week_numbers = QCheckBox("Show week numbers in calendar")
        self.show_week_numbers.setChecked(preferences.show_week_numbers)

        form.addRow("Date format", self.date_format)
        form.addRow("Time format", self.time_format)
        form.addRow("", self.show_week_numbers)

        form.addRow("Application updates", self.check_updates)
        return widget

    def _build_data_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(14)

        group = QGroupBox("Database location")
        group_layout = QFormLayout(group)
        db_path = database_path()
        db_label = QLabel(str(db_path))
        db_label.setTextInteractionFlags(db_label.textInteractionFlags())
        group_layout.addRow("Path:", db_label)

        open_button = QPushButton("Open folder")
        open_button.clicked.connect(self._open_db_folder)
        group_layout.addRow("", open_button)
        layout.addWidget(group)

        info_group = QGroupBox("Diagnostics")
        info_layout = QFormLayout(info_group)
        info_layout.addRow("Platform:", QLabel(platform.platform()))
        info_layout.addRow("Python:", QLabel(platform.python_version()))
        if self._scheduler is not None:
            task_count = str(len(self._scheduler.get_tasks()))
        else:
            task_count = "—"
        info_layout.addRow("Tasks:", QLabel(task_count))
        layout.addWidget(info_group)

        layout.addStretch()
        return widget

    def _build_about_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        build = load_build_info()
        title = QLabel("SchedPlus")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        version = QLabel(f"Version {build.version}")
        layout.addWidget(version)

        layout.addSpacing(10)

        desc = QLabel(
            "A local-first desktop task scheduler.\n\n"
            "All data is stored on your device. No accounts, no sync, "
            "no external services."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()
        return widget

    def _open_db_folder(self):
        folder = str(database_path().parent)
        import sys

        if sys.platform == "win32":
            import subprocess

            subprocess.Popen(["explorer", folder])
        elif sys.platform == "darwin":
            import subprocess

            subprocess.Popen(["open", folder])
        else:
            import subprocess

            subprocess.Popen(["xdg-open", folder])

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
            date_format=self.date_format.currentData(),
            time_format=self.time_format.currentData(),
            show_week_numbers=self.show_week_numbers.isChecked(),
        )

    def save_update_preferences(self) -> None:
        enabled = (
            self.check_updates.isChecked() if self.updates_managed_internally else False
        )
        save_update_preferences(
            UpdatePreferences(
                check_automatically=enabled,
            )
        )
