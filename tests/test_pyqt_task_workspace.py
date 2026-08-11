import os
from datetime import date, timedelta

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from logic.scheduler import Task
from ui.pyqt.add_dialog import EditTaskDialog
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

    assert dialog.get_values() == ("2026-08-12", "09:05", "Plan release")


def test_settings_dialog_round_trips_preferences(app):
    preferences = UiPreferences(
        sort_field="text",
        sort_order="descending",
        task_filter="upcoming",
        startup_view="calendar",
    )

    dialog = SettingsDialog(preferences)

    assert dialog.preferences() == preferences


def test_window_has_navigation_and_shortcuts(app):
    window = SchedPlusWindow(MemoryScheduler())

    assert window.pages.count() == 2
    assert len(window.shortcuts) == 7
    assert window.windowTitle() == "SchedPlus — Advanced"
