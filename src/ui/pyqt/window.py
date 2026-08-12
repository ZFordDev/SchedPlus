"""Primary advanced native window for SchedPlus."""

from dataclasses import replace

from PyQt6.QtCore import QObject, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from logic.storage.sqlite_storage import StorageError
from logic.validation import ValidationError
from updater.background import start_automatic_update
from updater.errors import UpdateError
from updater.service import launch_prepared_update
from ui.pyqt.add_dialog import AddTaskDialog, EditTaskDialog
from ui.pyqt.calendar_view import CalendarWorkspace
from ui.pyqt.settings_dialog import SettingsDialog, SettingsStore
from ui.pyqt.task_list import TaskListWidget
from ui.pyqt.theme import BASE_QSS


class _UpdateSignals(QObject):
    ready = pyqtSignal(object, object)
    failed = pyqtSignal(str)


class SchedPlusWindow(QMainWindow):
    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler
        self.settings_store = SettingsStore()
        self.preferences = self.settings_store.load()

        self.setWindowTitle("SchedPlus — Advanced")
        self.resize(1180, 760)
        self.setMinimumSize(820, 560)
        self.setStyleSheet(BASE_QSS)

        self.status_timer = QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.statusBar().clearMessage)

        root = QWidget()
        root.setObjectName("AppRoot")
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = self._build_sidebar()
        layout.addWidget(sidebar)

        self.pages = QStackedWidget()
        self.task_list = TaskListWidget(scheduler, self.preferences)
        self.calendar_page = CalendarWorkspace(scheduler, self.preferences)
        self.pages.addWidget(self.task_list)
        self.pages.addWidget(self.calendar_page)
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)

        self.task_list.add_requested.connect(self.open_add_dialog)
        self.task_list.edit_requested.connect(self.open_edit_dialog)
        self.task_list.delete_requested.connect(self.delete_task)
        self.calendar_page.add_requested.connect(self.open_add_dialog)
        self.calendar_page.edit_requested.connect(self.open_edit_dialog)
        self.calendar_page.delete_requested.connect(self.delete_task)
        self.calendar_page.reschedule_requested.connect(self.reschedule_task)

        self._create_shortcuts()
        self.show_page(self.preferences.startup_view)
        self.show_status_message("Tasks loaded")

        self.update_signals = _UpdateSignals(self)
        self.update_signals.ready.connect(self._offer_prepared_update)
        self.update_signals.failed.connect(
            lambda message: self.show_status_message(f"Update check failed: {message}")
        )
        self.update_thread = start_automatic_update(
            self.update_signals.ready.emit, self.update_signals.failed.emit
        )

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(210)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 20)
        layout.setSpacing(8)

        brand = QLabel("SchedPlus")
        brand.setObjectName("Brand")
        caption = QLabel("ADVANCED")
        caption.setObjectName("SidebarCaption")
        layout.addWidget(brand)
        layout.addWidget(caption)
        layout.addSpacing(22)

        self.tasks_nav = self._navigation_button("Tasks")
        self.calendar_nav = self._navigation_button("Calendar")
        self.settings_button = self._navigation_button("Settings")
        self.tasks_nav.clicked.connect(lambda: self.show_page("tasks"))
        self.calendar_nav.clicked.connect(lambda: self.show_page("calendar"))
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.tasks_nav)
        layout.addWidget(self.calendar_nav)
        layout.addStretch()
        layout.addWidget(self.settings_button)
        return sidebar

    def _navigation_button(self, text):
        button = QPushButton(text)
        button.setObjectName("NavigationButton")
        button.setCheckable(text != "Settings")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def _create_shortcuts(self):
        shortcuts = {
            "Ctrl+N": self.open_add_dialog,
            "Ctrl+E": self.edit_selected_task,
            "Delete": self.delete_selected_task,
            "Ctrl+R": self.reload_tasks,
            "Ctrl+F": self.task_list.focus_search,
            "Ctrl+,": self.open_settings,
            "F11": self.toggle_full_screen,
        }
        self.shortcuts = []
        for sequence, callback in shortcuts.items():
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)

    def show_page(self, page):
        calendar = page == "calendar"
        self.pages.setCurrentIndex(1 if calendar else 0)
        self.tasks_nav.setChecked(not calendar)
        self.calendar_nav.setChecked(calendar)

    def open_add_dialog(self, initial_date=None, initial_time=None):
        dialog = AddTaskDialog(
            self, initial_date=initial_date, initial_time=initial_time
        )
        if dialog.exec():
            date, time, text = dialog.get_values()
            try:
                self.scheduler.add_task(date, time, text)
                self.refresh_views()
                self.show_status_message("Task added successfully")
            except ValidationError as exc:
                self._show_validation_error(exc)
            except StorageError as exc:
                self._show_storage_error("Unable to add task", exc)

    def open_edit_dialog(self, task):
        draft = replace(task)
        dialog = EditTaskDialog(draft, self)
        if dialog.exec():
            draft.date, draft.time, draft.text = dialog.get_values()
            try:
                self.scheduler.update_task(draft)
                self.refresh_views()
                self.show_status_message("Task updated successfully")
            except ValidationError as exc:
                self._show_validation_error(exc)
            except StorageError as exc:
                self._show_storage_error("Unable to update task", exc)

    def delete_task(self, task):
        confirmation = QMessageBox(self)
        confirmation.setIcon(QMessageBox.Icon.Question)
        confirmation.setWindowTitle("Delete task?")
        confirmation.setText(f"Delete “{task.text}”?")
        confirmation.setInformativeText("This action cannot be undone.")
        confirmation.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        confirmation.setDefaultButton(QMessageBox.StandardButton.Cancel)
        confirmation.button(QMessageBox.StandardButton.Yes).setText("Delete")
        if confirmation.exec() != QMessageBox.StandardButton.Yes:
            return
        try:
            self.scheduler.delete_task(task.id)
            self.refresh_views()
            self.show_status_message("Task deleted")
        except StorageError as exc:
            self._show_storage_error("Unable to delete task", exc)

    def edit_selected_task(self):
        task = self.task_list.selected_task()
        if task:
            self.open_edit_dialog(task)
        else:
            self.show_status_message("Select a task to edit")

    def delete_selected_task(self):
        task = self.task_list.selected_task()
        if task:
            self.delete_task(task)
        else:
            self.show_status_message("Select a task to delete")

    def reload_tasks(self):
        try:
            self.scheduler.load_tasks()
            self.refresh_views()
            self.show_status_message("Tasks refreshed")
        except StorageError as exc:
            self._show_storage_error("Unable to refresh tasks", exc)

    def open_settings(self):
        dialog = SettingsDialog(self.preferences, self)
        if dialog.exec():
            self.preferences = dialog.preferences()
            self.settings_store.save(self.preferences)
            try:
                dialog.save_update_preferences()
            except UpdateError as exc:
                QMessageBox.warning(self, "Unable to save update settings", str(exc))
            self.task_list.apply_preferences(self.preferences)
            self.calendar_page.apply_preferences(self.preferences)
            self.show_page(self.preferences.startup_view)
            self.show_status_message("Settings saved")

    def _offer_prepared_update(self, build_info, prepared):
        prompt = QMessageBox(self)
        prompt.setIcon(QMessageBox.Icon.Information)
        prompt.setWindowTitle("SchedPlus update ready")
        prompt.setText(
            f"SchedPlus {prepared.check.latest_version} is ready to install."
        )
        prompt.setInformativeText(
            "SchedPlus will close and restart after installing the update."
        )
        prompt.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        prompt.button(QMessageBox.StandardButton.Yes).setText("Restart and update")
        prompt.button(QMessageBox.StandardButton.Cancel).setText("Later")
        prompt.setDefaultButton(QMessageBox.StandardButton.Yes)
        if prompt.exec() != QMessageBox.StandardButton.Yes:
            self.show_status_message("Update postponed")
            return
        try:
            launch_prepared_update(build_info, prepared)
        except UpdateError as exc:
            QMessageBox.critical(self, "Unable to install update", str(exc))
            return
        QApplication.instance().quit()

    def toggle_full_screen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def reschedule_task(self, task, date, time):
        draft = replace(task, date=date, time=time)
        try:
            self.scheduler.update_task(draft)
            self.refresh_views()
            self.show_status_message(f"Task moved to {date} at {time}")
        except ValidationError as exc:
            self.refresh_views()
            self._show_validation_error(exc)
        except StorageError as exc:
            self.refresh_views()
            self._show_storage_error("Unable to reschedule task", exc)

    def refresh_views(self):
        self.task_list.refresh()
        self.calendar_page.refresh()

    def show_status_message(self, message, duration=3500):
        self.statusBar().showMessage(f"  {message}")
        self.status_timer.start(duration)

    def _show_validation_error(self, error):
        self.show_status_message("Check task details")
        QMessageBox.warning(self, "Check task details", str(error))

    def _show_storage_error(self, title, error):
        self.show_status_message("Database operation failed")
        QMessageBox.critical(self, title, str(error))
