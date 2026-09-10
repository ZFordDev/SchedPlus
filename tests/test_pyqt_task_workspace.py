import os
from datetime import timedelta

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from logic import local_time
from logic.ical_import import ICSImportPlan, SkippedEvent
from logic.scheduler import Task
from ui.pyqt.add_dialog import AddTaskDialog, EditTaskDialog
from ui.pyqt.calendar_view import CalendarWorkspace
from ui.pyqt.ics_import_dialog import IcsImportDialog
from ui.pyqt.settings_dialog import SettingsDialog, UiPreferences
from ui.pyqt.task_list import TaskListWidget, TaskTableModel
from ui.pyqt.window import SchedPlusWindow
from updater.config import BuildInfo
from updater.preferences import UpdatePreferences


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


def test_theme_installs_brand_palette_and_covers_core_widgets(app):
    from PyQt6.QtGui import QPalette

    from ui.pyqt.theme import BASE_QSS, install_theme

    install_theme(app)
    palette = app.palette()
    assert palette.color(QPalette.ColorRole.Window).name() == "#f4f6f8"
    assert palette.color(QPalette.ColorRole.Base).name() == "#ffffff"
    assert palette.color(QPalette.ColorRole.AlternateBase).name() == "#f8fafc"
    assert palette.color(QPalette.ColorRole.WindowText).name() == "#172033"
    disabled_text = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text)
    assert disabled_text.name() == "#94a3b8"

    for selector in (
        "QScrollBar",
        "QMenuBar",
        "QMenu",
        "QSpinBox",
        "QTabWidget",
        "QTabBar",
        "QGroupBox",
        "QCheckBox",
        "QToolTip",
        "QSplitter",
        "QDialogButtonBox",
        "QCalendarWidget",
    ):
        assert selector in BASE_QSS, selector


def test_task_workspace_filters_and_searches(app):
    today = local_time.today()
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


def test_task_table_model_respects_root_and_child_indexes(app):
    model = TaskTableModel([Task(date="2026-08-28", time="09:00", text="Plan")])

    assert model.rowCount() == 1
    assert model.columnCount() == 5

    child_index = model.index(0, 0)
    assert child_index.isValid()
    assert model.rowCount(child_index) == 0
    assert model.columnCount(child_index) == 0


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


def test_settings_dialog_opens_large_with_scrollable_tabs(app):
    from PyQt6.QtWidgets import QScrollArea, QTabWidget

    dialog = SettingsDialog(UiPreferences())

    assert dialog.width() >= 560
    assert dialog.height() >= 620

    tabs = dialog.findChild(QTabWidget)
    assert tabs.count() == 3
    for index in range(tabs.count()):
        page = tabs.widget(index)
        assert isinstance(page, QScrollArea), index
        assert page.widgetResizable()
        assert page.widget() is not None


def test_update_preference_stays_off_for_store_builds(app, monkeypatch):
    # A source checkout has no embedded build-info.json, so it behaves like an
    # externally managed store build (Snap/MSIX).
    monkeypatch.setattr(
        "ui.pyqt.settings_dialog.load_update_preferences",
        lambda: UpdatePreferences(check_automatically=True),
    )
    saved = []
    monkeypatch.setattr(
        "ui.pyqt.settings_dialog.save_update_preferences",
        saved.append,
    )

    dialog = SettingsDialog(UiPreferences())

    assert not dialog.updates_managed_internally
    assert not dialog.check_updates.isChecked()
    assert not dialog.check_updates.isEnabled()

    dialog.save_update_preferences()
    assert saved == [UpdatePreferences(check_automatically=False)]


def test_update_preference_remains_editable_for_managed_builds(app, monkeypatch):
    managed = BuildInfo(version="0.0.0", package_format="source", updates_enabled=True)
    assert managed.internally_managed
    monkeypatch.setattr("ui.pyqt.settings_dialog.load_build_info", lambda: managed)
    monkeypatch.setattr(
        "ui.pyqt.settings_dialog.load_update_preferences",
        lambda: UpdatePreferences(check_automatically=True),
    )
    saved = []
    monkeypatch.setattr(
        "ui.pyqt.settings_dialog.save_update_preferences",
        saved.append,
    )

    dialog = SettingsDialog(UiPreferences())

    assert dialog.updates_managed_internally
    assert dialog.check_updates.isChecked()
    assert dialog.check_updates.isEnabled()

    dialog.check_updates.setChecked(False)
    dialog.save_update_preferences()
    assert saved == [UpdatePreferences(check_automatically=False)]


def test_window_has_navigation_and_shortcuts(app):
    window = SchedPlusWindow(MemoryScheduler())

    assert window.pages.count() == 2
    assert len(window.shortcuts) == 10
    assert window.windowTitle() == "SchedPlus — Advanced"
    assert window.version_label.text().startswith("SchedPlus v")
    assert window.about_action.text() == "About SchedPlus"


def test_native_calendar_renders_month_week_and_day(app):
    today = local_time.today()
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
    task = Task(date=local_time.today().isoformat(), time="09:30", text="Move task")
    workspace = CalendarWorkspace(MemoryScheduler([task]), UiPreferences())
    requests = []
    workspace.reschedule_requested.connect(
        lambda moved, new_date, new_time: requests.append((moved, new_date, new_time))
    )

    workspace.week_table.task_dropped.emit(task, "2026-09-14", "13:30")

    assert requests == [(task, "2026-09-14", "13:30")]


def test_today_button_is_styled_and_accessible(app):
    workspace = CalendarWorkspace(MemoryScheduler(), UiPreferences())

    assert workspace.today_button.objectName() == "PrimaryButton"
    assert workspace.today_button.accessibleName() == "Go to today"
    assert workspace.today_button.toolTip() == "Return to today's date"


def test_go_to_today_returns_to_current_date_in_all_views(app):
    today = local_time.today()
    scheduler = MemoryScheduler(
        [Task(date=today.isoformat(), time="09:00", text="Anchor task")]
    )
    workspace = CalendarWorkspace(scheduler, UiPreferences())
    future_date = today + timedelta(days=45)

    for view in ("month", "week", "day"):
        workspace.view_combo.setCurrentIndex(workspace.view_combo.findData(view))
        workspace.month_calendar.setSelectedDate(future_date)
        workspace.month_calendar.setCurrentPage(future_date.year, future_date.month)
        workspace.refresh()

        assert workspace.month_calendar.selectedDate().toPyDate() == future_date

        workspace.go_to_today()

        assert workspace.month_calendar.selectedDate().toPyDate() == today
        assert today.isoformat() in workspace.week_table.slot_dates or view != "week"
        assert workspace.month_calendar.monthShown() == today.month
        assert workspace.month_calendar.yearShown() == today.year


def test_today_button_remains_visible_after_navigating_away(app):
    workspace = CalendarWorkspace(MemoryScheduler(), UiPreferences())
    future_date = local_time.today() + timedelta(days=90)

    workspace.month_calendar.setSelectedDate(future_date)
    workspace.month_calendar.setCurrentPage(future_date.year, future_date.month)
    workspace.refresh()

    assert not workspace.today_button.isHidden()


def _ics_plan():
    return ICSImportPlan(
        tasks=[
            Task(date="2026-09-11", time="14:00", text="Standup"),
            Task(date="2026-09-12", time="09:00", text="Planning"),
        ],
        duplicates=1,
        skipped=[SkippedEvent("Repeats", "recurring")],
        event_count=4,
    )


def test_ics_import_dialog_previews_and_confirms_selection(app):
    dialog = IcsImportDialog(_ics_plan())

    assert dialog.table.rowCount() == 4
    assert dialog.confirmed_tasks() == dialog._plan.tasks
    assert dialog.import_button.isEnabled()

    dialog._checks[0].setChecked(False)
    confirmed = dialog.confirmed_tasks()
    assert [task.text for task in confirmed] == ["Planning"]


def test_ics_import_dialog_disables_import_when_nothing_selected(app):
    dialog = IcsImportDialog(_ics_plan())

    for check in dialog._checks:
        check.setChecked(False)

    assert not dialog.import_button.isEnabled()
    assert dialog.confirmed_tasks() == []
