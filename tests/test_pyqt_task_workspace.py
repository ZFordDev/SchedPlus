import os
from datetime import timedelta

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QMimeData, Qt
from PyQt6.QtWidgets import QApplication, QLabel

from logic import local_time
from logic.ical_import import ICSImportPlan, SkippedEvent
from logic.scheduler import Scheduler, Task
from logic.storage import sqlite_storage as storage
from ui.pyqt.add_dialog import AddTaskDialog, EditTaskDialog
from ui.pyqt.board_view import BOARD_MIME_TYPE, BoardCard, BoardColumn, BoardView
from ui.pyqt.calendar_view import CalendarWorkspace
from ui.pyqt.ics_import_dialog import IcsImportDialog
from ui.pyqt.settings_dialog import SettingsDialog, UiPreferences
from ui.pyqt.task_list import TaskFilterProxyModel, TaskListWidget, TaskTableModel
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


@pytest.fixture
def task_database(monkeypatch, tmp_path):
    path = tmp_path / "data" / "tasks.db"
    path.parent.mkdir()
    monkeypatch.setattr(storage, "prepare_database", lambda: path)
    monkeypatch.setattr(storage, "_configure_logging", lambda _directory: None)
    return path


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

    assert window.pages.count() == 3
    assert len(window.shortcuts) == 10
    assert window.windowTitle() == "SchedPlus — Advanced"
    assert window.version_label.text().startswith("SchedPlus v")
    assert window.about_action.text() == "About SchedPlus"
    assert window.board_nav.text() == "Kanban"
    assert window.board_nav.accessibleName() == "Switch to Kanban view"

    window.show_page("board")

    assert window.pages.currentIndex() == 2
    assert window.board_nav.isChecked()
    assert not window.tasks_nav.isChecked()


def test_board_lists_only_opted_in_tasks(app):
    scheduler = MemoryScheduler(
        [
            Task(
                date="2026-09-11",
                time="09:00",
                text="Backlog card",
                board_stage="backlog",
            ),
            Task(
                date="2026-09-12",
                time="10:00",
                text="Doing card",
                board_stage="in_progress",
            ),
            Task(date="2026-09-13", time="11:00", text="Done card", board_stage="done"),
            Task(date="2026-09-14", time="12:00", text="Off board card"),
        ]
    )
    board = BoardView(scheduler)

    assert board.columns["backlog"].card_layout.count() == 2
    assert board.columns["in_progress"].card_layout.count() == 2
    assert board.columns["done"].card_layout.count() == 2
    assert board.empty_label.isHidden()
    assert not board.columns_widget.isHidden()
    assert board.columns["backlog"].empty_label.isHidden()
    assert "3 of 4 tasks" in board.count_label.text()


def test_board_empty_state(app):
    board = BoardView(MemoryScheduler())

    assert not board.empty_label.isHidden()
    assert board.columns_widget.isHidden()
    assert "No tasks on the board" in board.empty_label.text()


def test_board_column_cards_forward_signals(app):
    task = Task(date="2026-09-11", time="09:00", text="Card", board_stage="backlog")
    column = BoardColumn("backlog")
    column.set_tasks([task])
    emitted = []
    column.complete_requested.connect(emitted.append)

    card_layout = column.card_layout
    card = card_layout.itemAt(0).widget()
    card.complete_button.click()

    assert emitted == [task]


def test_board_reflects_refreshed_scheduler(app):
    scheduler = MemoryScheduler()
    board = BoardView(scheduler)
    assert board.columns_widget.isHidden()

    scheduler.tasks.append(
        Task(date="2026-09-11", time="09:00", text="New card", board_stage="done")
    )
    board.refresh()

    assert not board.columns_widget.isHidden()
    assert board.columns["done"].card_layout.count() == 2
    assert "1 of 1 tasks" in board.count_label.text()


def test_board_card_mime_carries_task_id(app):
    task = Task(date="2026-09-11", time="09:00", text="Card")
    card = BoardCard(task)

    assert card.drag_mime(task).hasFormat(BOARD_MIME_TYPE)
    assert bytes(card.drag_mime(task).data(BOARD_MIME_TYPE)).decode("utf-8") == task.id


def test_board_column_accepts_task_drops(app):
    from PyQt6.QtCore import QPoint, QPointF
    from PyQt6.QtGui import QDragEnterEvent, QDropEvent

    column = BoardColumn("backlog")
    moved = []
    column.move_requested.connect(lambda task_id, stage: moved.append((task_id, stage)))

    mime = QMimeData()
    mime.setData(BOARD_MIME_TYPE, b"task-1")
    enter = QDragEnterEvent(
        QPoint(4, 4),
        Qt.DropAction.MoveAction,
        mime,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    column.dragEnterEvent(enter)
    assert enter.isAccepted()

    drop = QDropEvent(
        QPointF(4, 4),
        Qt.DropAction.MoveAction,
        mime,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    column.dropEvent(drop)

    assert drop.isAccepted()
    assert moved == [("task-1", "backlog")]


def test_board_view_resolves_column_move_to_task(app):
    task = Task(date="2026-09-11", time="09:00", text="Card", board_stage="backlog")
    board = BoardView(MemoryScheduler([task]))
    emitted = []
    board.move_requested.connect(lambda moved, stage: emitted.append((moved, stage)))

    board.columns["backlog"].move_requested.emit(task.id, "done")

    assert emitted == [(task, "done")]


def test_window_board_move_persists_without_touching_completion(app, task_database):
    storage.initialize_database()
    scheduler = Scheduler()
    task = scheduler.add_task(
        "2026-09-11", "09:00", "Plan release", board_stage="backlog"
    )
    window = SchedPlusWindow(scheduler)

    window.move_board_task(task, "done")

    persisted = scheduler.load_tasks()[0]
    assert persisted.board_stage == "done"
    assert persisted.completed == task.completed
    assert window.board_page.columns["done"].card_layout.count() == 2


def test_window_board_move_to_same_column_is_noop(app, task_database):
    storage.initialize_database()
    scheduler = Scheduler()
    task = scheduler.add_task(
        "2026-09-11", "09:00", "Plan release", board_stage="backlog"
    )
    window = SchedPlusWindow(scheduler)

    window.move_board_task(task, "backlog")

    assert scheduler.load_tasks()[0].board_stage == "backlog"


def test_window_undo_reverts_board_move(app, task_database):
    storage.initialize_database()
    scheduler = Scheduler()
    task = scheduler.add_task(
        "2026-09-11", "09:00", "Plan release", board_stage="backlog"
    )
    window = SchedPlusWindow(scheduler)

    window.move_board_task(task, "done")
    assert scheduler.load_tasks()[0].board_stage == "done"

    scheduler.undo_manager.undo()

    assert scheduler.load_tasks()[0].board_stage == "backlog"


def test_board_column_set_tasks_evicts_stale_cards(app):
    column = BoardColumn("backlog")
    column.set_tasks([Task(date="2026-09-11", time="09:00", text="Card")])
    stale = column.card_layout.itemAt(0).widget()

    column.set_tasks([])

    assert not stale.isVisible()
    assert column.card_layout.count() == 1
    for index in range(column.card_layout.count()):
        assert column.card_layout.itemAt(index).widget() is None


def test_board_refresh_does_not_keep_moved_card_in_source_column(app):
    task = Task(date="2026-09-11", time="09:00", text="Card", board_stage="backlog")
    scheduler = MemoryScheduler([task])
    board = BoardView(scheduler)
    stored = scheduler.load_tasks()
    stored[0] = Task(
        id=task.id,
        date=task.date,
        time=task.time,
        text=task.text,
        createdAt=task.createdAt,
        updatedAt=task.updatedAt,
        board_stage="done",
    )

    board.refresh()

    assert board.columns["done"].card_layout.count() == 2
    assert board.columns["backlog"].card_layout.count() == 1
    assert not board.columns["backlog"].empty_label.isHidden()


def test_task_proxy_filters_on_board_only(app):
    model = TaskTableModel(
        [
            Task(date="2026-09-11", time="09:00", text="On cards", board_stage="done"),
            Task(date="2026-09-12", time="10:00", text="Plain row"),
        ]
    )
    proxy = TaskFilterProxyModel()
    proxy.setSourceModel(model)
    proxy.set_task_filter("board")

    assert proxy.rowCount() == 1
    assert proxy.index(0, 0).data(Qt.ItemDataRole.UserRole).text == "On cards"


def test_settings_offer_board_filter_and_kanban_startup(app):
    dialog = SettingsDialog(UiPreferences())

    assert dialog.task_filter.findData("board") != -1
    assert dialog.startup_view.findData("board") != -1


def test_board_search_filters_cards(app):
    scheduler = MemoryScheduler(
        [
            Task(
                date="2026-09-11",
                time="09:00",
                text="Plan release",
                board_stage="backlog",
            ),
            Task(
                date="2026-09-12",
                time="10:00",
                text="Write tests",
                board_stage="in_progress",
            ),
        ]
    )
    board = BoardView(scheduler)

    board.search_input.setText("release")

    assert board.columns["backlog"].card_layout.count() == 2
    assert board.columns["in_progress"].card_layout.count() == 1
    assert "1 of 2 tasks match on the board" in board.count_label.text()

    board.search_input.setText("zzz")

    assert board.columns_widget.isHidden()
    assert not board.empty_label.isHidden()
    assert "No cards match the search." in board.empty_label.text()

    board.search_input.clear()

    assert not board.columns_widget.isHidden()
    assert "2 of 2 tasks on the board" in board.count_label.text()


def test_board_card_keyboard_enter_edits_and_delete_deletes(app):
    from PyQt6.QtTest import QTest

    task = Task(date="2026-09-11", time="09:00", text="Card", board_stage="backlog")
    column = BoardColumn("backlog")
    column.set_tasks([task])
    card = column.card_layout.itemAt(0).widget()
    edited = []
    deleted = []
    card.edit_requested.connect(edited.append)
    card.delete_requested.connect(deleted.append)

    QTest.keyClick(card, Qt.Key.Key_Return)
    QTest.keyClick(card, Qt.Key.Key_Delete)

    assert edited == [task]
    assert deleted == [task]


def test_board_arrow_keys_navigate_between_columns(app):
    scheduler = MemoryScheduler(
        [
            Task(
                date="2026-09-11",
                time="09:00",
                text="Backlog card",
                board_stage="backlog",
            ),
            Task(
                date="2026-09-11",
                time="09:30",
                text="Second backlog",
                board_stage="backlog",
            ),
            Task(
                date="2026-09-12",
                time="10:00",
                text="Doing card",
                board_stage="in_progress",
            ),
            Task(
                date="2026-09-13",
                time="11:00",
                text="Done card",
                board_stage="done",
            ),
        ]
    )
    board = BoardView(scheduler)
    backlog, backlog_two = board._cards("backlog")
    doing = board._cards("in_progress")[0]
    done = board._cards("done")[0]

    assert board._nav_target(backlog, column_delta=1) is doing
    assert board._nav_target(backlog, column_delta=2) is done
    assert board._nav_target(done, column_delta=-2) is backlog
    assert board._nav_target(backlog_two, row_delta=-1) is backlog
    assert board._nav_target(backlog, row_delta=1) is backlog_two
    assert board._nav_target(backlog, row_delta=-1) is backlog
    assert board._nav_target(backlog_two, row_delta=1) is backlog_two


def test_window_complete_reflects_on_board_and_task_list(app, task_database):
    storage.initialize_database()
    scheduler = Scheduler()
    task = scheduler.add_task(
        "2026-09-11", "09:00", "Plan release", board_stage="backlog"
    )
    window = SchedPlusWindow(scheduler)

    window.complete_task(task)

    assert scheduler.load_tasks()[0].completed == "true"
    assert window.board_page.columns["backlog"].card_layout.count() == 2
    assert window.task_list.model.tasks[0].completed == "true"


def test_add_dialog_boards_task_when_checked(app):
    dialog = AddTaskDialog()

    assert dialog.get_values()[10] == ""
    assert not dialog.board_combo.isEnabled()

    dialog.board_checkbox.setChecked(True)
    dialog.board_combo.setCurrentIndex(dialog.board_combo.findData("in_progress"))

    assert dialog.board_combo.isEnabled()
    assert dialog.get_values()[10] == "in_progress"


def test_edit_dialog_preselects_and_clears_board_stage(app):
    task = Task(date="2026-09-11", time="09:00", text="Board task", board_stage="done")
    dialog = EditTaskDialog(task)

    assert dialog.board_checkbox.isChecked()
    assert dialog.get_values()[10] == "done"

    dialog.board_checkbox.setChecked(False)

    assert not dialog.board_combo.isEnabled()
    assert dialog.get_values()[10] == ""


def test_edit_dialog_defaults_unchecked_for_off_board_tasks(app):
    task = Task(date="2026-09-11", time="09:00", text="Plain task")
    dialog = EditTaskDialog(task)

    assert not dialog.board_checkbox.isChecked()
    assert dialog.get_values()[10] == ""


def test_add_dialog_unscheduled_yields_empty_date_and_time(app):
    dialog = AddTaskDialog()

    assert not dialog.unscheduled_checkbox.isChecked()
    assert dialog.date_input.isEnabled()

    dialog.unscheduled_checkbox.setChecked(True)

    assert not dialog.date_input.isEnabled()
    assert not dialog.time_input.isEnabled()
    values = dialog.get_values()
    assert values[0] == ""
    assert values[1] == ""


def test_edit_dialog_preselects_unscheduled_for_dateless_task(app):
    task = Task(date="", time="", text="Planning card", board_stage="backlog")
    dialog = EditTaskDialog(task)

    assert dialog.unscheduled_checkbox.isChecked()
    assert not dialog.date_input.isEnabled()
    assert dialog.get_values()[0] == ""


def test_unscheduled_dialogs_disable_repeat_controls(app):
    task = Task(date="", time="", text="Planning card", board_stage="backlog")
    dialog = EditTaskDialog(task)

    dialog.unscheduled_checkbox.setChecked(False)
    assert dialog.recurrence_input.isEnabled()
    assert dialog.recurrence_end_input.isEnabled()

    dialog.unscheduled_checkbox.setChecked(True)
    assert not dialog.recurrence_input.isEnabled()
    assert not dialog.recurrence_end_input.isEnabled()


def test_board_card_marks_dateless_task_unscheduled(app):
    task = Task(text="Planning card", board_stage="backlog")
    column = BoardColumn("backlog")
    column.set_tasks([task])
    card = column.card_layout.itemAt(0).widget()

    assert any(label.text() == "Unscheduled" for label in card.findChildren(QLabel))


def test_task_proxy_filters_exclude_unscheduled_from_date_filters(app):
    today = local_time.today().isoformat()
    model = TaskTableModel(
        [
            Task(date="", time="", text="Planning card", board_stage="backlog"),
            Task(date=today, time="09:00", text="Today task"),
        ]
    )
    proxy = TaskFilterProxyModel()
    proxy.setSourceModel(model)

    proxy.set_task_filter("today")
    assert proxy.rowCount() == 1
    assert proxy.index(0, 0).data(Qt.ItemDataRole.UserRole).text == "Today task"

    proxy.set_task_filter("upcoming")
    assert proxy.rowCount() == 1


def test_task_proxy_scheduled_filter_excludes_unscheduled(app):
    model = TaskTableModel(
        [
            Task(date="", time="", text="Planning card", board_stage="backlog"),
            Task(date="2026-01-01", time="09:00", text="Dated task"),
        ]
    )
    proxy = TaskFilterProxyModel()
    proxy.setSourceModel(model)

    proxy.set_task_filter("all")
    assert proxy.rowCount() == 2

    proxy.set_task_filter("scheduled")
    assert proxy.rowCount() == 1
    assert proxy.index(0, 0).data(Qt.ItemDataRole.UserRole).text == "Dated task"


def test_task_proxy_sorts_unscheduled_as_now(app):
    today = local_time.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    tasks = [
        Task(date=tomorrow.isoformat(), time="23:59", text="Future task"),
        Task(date="", time="", text="Planning card", board_stage="backlog"),
        Task(date=yesterday.isoformat(), time="00:01", text="Past task"),
        Task(date=today.isoformat(), time="12:00", text="Today task"),
    ]
    model = TaskTableModel(tasks)
    proxy = TaskFilterProxyModel()
    proxy.setSourceModel(model)
    proxy.sort(0, Qt.SortOrder.AscendingOrder)

    ordered = [
        proxy.index(row, 0).data(Qt.ItemDataRole.UserRole).text
        for row in range(proxy.rowCount())
    ]
    assert ordered.index("Planning card") > ordered.index("Past task")
    assert ordered.index("Planning card") < ordered.index("Future task")
    assert ordered[0] == "Past task"
    assert ordered[-1] == "Future task"


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
