import os
from datetime import date, timedelta

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from logic.scheduler import Task
from ui.pyqt.add_dialog import AddTaskDialog, EditTaskDialog
from ui.pyqt.calendar_view import CalendarWorkspace
from ui.pyqt.settings_dialog import SettingsDialog, UiPreferences
from ui.pyqt.task_list import TaskListWidget
from ui.pyqt.window import SchedPlusWindow


class MemoryScheduler:
    def __init__(self, tasks=None):
        self.tasks = list(tasks or [])

    def get_tasks(self):
        return self.tasks

    def load_tasks(self):
        return self.tasks


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    yield application


def test_task_workspace_filters_and_searches(app):
    today = date.today()
    scheduler = MemoryScheduler(
        [
            Task(date=today.isoformat(), time="09:00", text="Today task"),
            Task(
                date=(today + timedelta(days=1)).isoformat(),
                time="10:00",
                text="Future planning",
            ),
            Task(
                date=(today - timedelta(days=1)).isoformat(),
                time="11:00",
                text="Past task",
            ),
        ]
    )
    widget = TaskListWidget(scheduler, UiPreferences())

    assert widget.proxy.rowCount() == 3
    widget.filter_combo.setCurrentIndex(widget.filter_combo.findData("today"))
    assert widget.proxy.rowCount() == 1
    widget.filter_combo.setCurrentIndex(widget.filter_combo.findData("all"))
    widget.search_input.setText("planning")
    assert widget.proxy.rowCount() == 1
    assert "1 of 3" in widget.count_label.text()


def test_edit_dialog_is_prepopulated(app):
    task = Task(date="2026-08-12", time="09:05", text="Plan release")

    dialog = EditTaskDialog(task)

    values = dialog.get_values()
    assert values[0] == "2026-08-12"
    assert values[1] == "09:05"
    assert values[2] == "Plan release"


def test_add_dialog_accepts_calendar_slot_defaults(app):
    dialog = AddTaskDialog(initial_date="2026-09-14", initial_time="13:30")

    values = dialog.get_values()
    assert values[0] == "2026-09-14"
    assert values[1] == "13:30"
    assert values[2] == ""


def test_settings_dialog_round_trips_preferences(app):
    preferences = UiPreferences(
        sort_field="text",
        sort_order="descending",
        task_filter="upcoming",
        startup_view="calendar",
        calendar_view="week",
        first_day_of_week="sunday",
        workday_start=6,
        workday_end=22,
        date_format="MM/dd/yyyy",
        time_format="h:mm AP",
        show_week_numbers=False,
    )

    dialog = SettingsDialog(preferences)

    assert dialog.preferences() == preferences


def test_window_has_navigation_and_shortcuts(app):
    window = SchedPlusWindow(MemoryScheduler())

    assert window.pages.count() == 2
    assert len(window.shortcuts) == 9
    assert window.windowTitle() == "SchedPlus — Advanced"
    assert window.version_label.text().startswith("SchedPlus v")
    assert window.about_action.text() == "About SchedPlus"


def test_native_calendar_renders_month_week_and_day(app):
    today = date.today()
    scheduler = MemoryScheduler(
        [
            Task(date=today.isoformat(), time="09:30", text="Calendar task"),
            Task(date=today.isoformat(), time="23:45", text="Late task"),
        ]
    )
    workspace = CalendarWorkspace(scheduler, UiPreferences())

    assert workspace.month_calendar.task_counts[today.isoformat()] == 2
    assert workspace.month_agenda.count() == 2
    assert not workspace.month_agenda.isHidden()
    assert workspace.month_empty.isHidden()

    workspace.view_combo.setCurrentIndex(workspace.view_combo.findData("week"))
    assert workspace.week_table.columnCount() == 7
    assert today.isoformat() in workspace.week_table.slot_dates
    assert "23:30" in workspace.week_table.slot_times

    workspace.view_combo.setCurrentIndex(workspace.view_combo.findData("day"))
    assert workspace.day_table.columnCount() == 1
    assert workspace.day_table.slot_dates == [today.isoformat()]

    workspace.month_calendar.setSelectedDate(
        workspace.month_calendar.selectedDate().addDays(30)
    )
    assert workspace.month_agenda.isHidden()
    assert not workspace.month_empty.isHidden()


def test_calendar_emits_reschedule_request(app):
    task = Task(date=date.today().isoformat(), time="09:30", text="Move task")
    workspace = CalendarWorkspace(MemoryScheduler([task]), UiPreferences())
    requests = []
    workspace.reschedule_requested.connect(
        lambda moved, new_date, new_time: requests.append((moved, new_date, new_time))
    )

    workspace.week_table.task_dropped.emit(task, "2026-09-14", "13:30")

    assert requests == [(task, "2026-09-14", "13:30")]
