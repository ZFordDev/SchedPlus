"""Primary advanced native window for SchedPlus."""

from dataclasses import asdict, replace
from pathlib import Path

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from logic.data_transfer import (
    DataTransferError,
    create_backup,
    export_tasks,
    import_tasks,
    restore_backup,
)
from logic.storage.sqlite_storage import StorageError
from logic.validation import ValidationError
from schedplus.identity import get_application_identity
from ui.pyqt.add_dialog import AddTaskDialog, EditTaskDialog
from ui.pyqt.calendar_view import CalendarWorkspace
from ui.pyqt.settings_dialog import SettingsDialog, SettingsStore, UiPreferences
from ui.pyqt.task_list import TaskListWidget
from ui.pyqt.theme import BASE_QSS
from updater.background import start_automatic_update, start_update_check
from updater.errors import UpdateError
from updater.service import launch_prepared_update
from updater.state import read_state


class _UpdateSignals(QObject):
    ready = pyqtSignal(object, object)
    failed = pyqtSignal(str)


class SchedPlusWindow(QMainWindow):
    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler
        self.identity = get_application_identity()
        self.settings_store = SettingsStore()
        self.preferences = self.settings_store.load()

        self.setWindowTitle("SchedPlus — Advanced")
        self.resize(1180, 760)
        self.setMinimumSize(820, 560)
        self.setStyleSheet(BASE_QSS)

        data_menu = self.menuBar().addMenu("Data")
        self.backup_action = data_menu.addAction("Create backup…")
        self.restore_action = data_menu.addAction("Restore backup…")
        data_menu.addSeparator()
        self.export_action = data_menu.addAction("Export tasks…")
        self.import_action = data_menu.addAction("Import tasks…")
        self.backup_action.triggered.connect(self.backup_data)
        self.restore_action.triggered.connect(self.restore_data)
        self.export_action.triggered.connect(self.export_data)
        self.import_action.triggered.connect(self.import_data)

        help_menu = self.menuBar().addMenu("Help")
        self.check_update_action = help_menu.addAction("Check for updates")
        self.update_status_action = help_menu.addAction("Last update result")
        help_menu.addSeparator()
        self.shortcuts_action = help_menu.addAction("Keyboard shortcuts")
        self.about_action = help_menu.addAction("About SchedPlus")
        self.check_update_action.triggered.connect(self.check_for_updates)
        self.update_status_action.triggered.connect(self.show_update_status)
        self.shortcuts_action.triggered.connect(self.show_shortcuts)
        self.about_action.triggered.connect(self.show_about)

        self.backup_action.setAccessibleName("Create backup of all tasks and settings")
        self.restore_action.setAccessibleName("Restore tasks and settings from a backup file")
        self.export_action.setAccessibleName("Export tasks to a JSON file")
        self.import_action.setAccessibleName("Import tasks from a JSON file")
        self.check_update_action.setAccessibleName("Check for application updates")
        self.update_status_action.setAccessibleName("Show last update check result")
        self.about_action.setAccessibleName("Show application information")

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
        self.task_list.complete_requested.connect(self.complete_task)
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
        self.tasks_nav.setAccessibleName("Switch to Tasks view")
        self.calendar_nav.setAccessibleName("Switch to Calendar view")
        self.settings_button.setAccessibleName("Open settings")
        self.tasks_nav.clicked.connect(lambda: self.show_page("tasks"))
        self.calendar_nav.clicked.connect(lambda: self.show_page("calendar"))
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.tasks_nav)
        layout.addWidget(self.calendar_nav)
        layout.addStretch()
        layout.addWidget(self.settings_button)
        self.version_label = QLabel(self.identity.version_label)
        self.version_label.setObjectName("SidebarVersion")
        layout.addWidget(self.version_label)
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
            "Ctrl+Z": self.undo_last_action,
            "Ctrl+Q": self.close,
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
            self, initial_date=initial_date, initial_time=initial_time,
            date_format=self.preferences.date_format,
            time_format=self.preferences.time_format,
        )
        if dialog.exec():
            date, time, text, notes, priority, duration, category, recurrence, recurrence_end, reminder = dialog.get_values()
            try:
                task = self.scheduler.add_task(date, time, text)
                if notes or priority or duration or category or recurrence or reminder:
                    from dataclasses import replace
                    task = replace(task, notes=notes, priority=priority, duration=duration, category=category, recurrence=recurrence, recurrenceEnd=recurrence_end, reminder=reminder)
                    self.scheduler.update_task(task)
                self.scheduler.undo_manager.record_add(task.id)
                self.refresh_views()
                self.show_status_message("Task added successfully")
            except ValidationError as exc:
                self._show_validation_error(exc)
            except StorageError as exc:
                self._show_storage_error("Unable to add task", exc)

    def open_edit_dialog(self, task):
        from dataclasses import replace as dc_replace
        draft = dc_replace(task)
        dialog = EditTaskDialog(draft, self,
            date_format=self.preferences.date_format,
            time_format=self.preferences.time_format,
        )
        if dialog.exec():
            draft.date, draft.time, draft.text, draft.notes, draft.priority, draft.duration, draft.category, draft.recurrence, draft.recurrenceEnd, draft.reminder = dialog.get_values()
            try:
                self.scheduler.undo_manager.record_edit(task)
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
        confirmation.setText(f"Delete "{task.text}"?")
        confirmation.setInformativeText("This action cannot be undone.")
        confirmation.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        confirmation.setDefaultButton(QMessageBox.StandardButton.Cancel)
        confirmation.button(QMessageBox.StandardButton.Yes).setText("Delete")
        if confirmation.exec() != QMessageBox.StandardButton.Yes:
            return
        try:
            self.scheduler.undo_manager.record_delete(task)
            self.scheduler.delete_task(task.id)
            self.refresh_views()
            self.show_status_message("Task deleted")
        except StorageError as exc:
            self._show_storage_error("Unable to delete task", exc)

    def complete_task(self, task):
        try:
            if task.completed == "true":
                self.scheduler.undo_manager.record_uncomplete(task.id)
                self.scheduler.uncomplete_task(task.id)
                self.refresh_views()
                self.show_status_message("Task marked as incomplete")
            else:
                self.scheduler.undo_manager.record_complete(task.id)
                self.scheduler.complete_task(task.id)
                self.refresh_views()
                self.show_status_message("Task marked as complete")
        except StorageError as exc:
            self._show_storage_error("Unable to update task", exc)

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
            try:
                self.settings_store.save(self.preferences)
                dialog.save_update_preferences()
            except (DataTransferError, UpdateError) as exc:
                QMessageBox.warning(self, "Unable to save settings", str(exc))
            self.task_list.apply_preferences(self.preferences)
            self.calendar_page.apply_preferences(self.preferences)
            self.show_page(self.preferences.startup_view)
            self.show_status_message("Settings saved")

    def backup_data(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Create SchedPlus backup", "SchedPlus-backup.json", "JSON (*.json)"
        )
        if path:
            self._run_data_action(
                "Backup created",
                lambda: create_backup(Path(path), ui_preferences=asdict(self.preferences)),
            )

    def restore_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Restore SchedPlus backup", "", "JSON (*.json)"
        )
        if not path or QMessageBox.question(
            self,
            "Replace current data?",
            "Restore will replace all current tasks and preferences. Continue?",
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            result = restore_backup(
                Path(path), current_ui_preferences=asdict(self.preferences)
            )
            if result.ui_preferences is not None:
                self.preferences = UiPreferences(**result.ui_preferences)
                self.settings_store.save(self.preferences)
            self.scheduler.load_tasks()
            self.refresh_views()
            QMessageBox.information(
                self,
                "Backup restored",
                f"Restored {result.restored} task(s).\n\n"
                f"Previous data was backed up to:\n{result.safety_backup}",
            )
        except (DataTransferError, StorageError, TypeError) as exc:
            QMessageBox.critical(self, "Unable to restore backup", str(exc))

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export SchedPlus tasks", "SchedPlus-tasks.json", "JSON (*.json)"
        )
        if path:
            self._run_data_action("Tasks exported", lambda: export_tasks(Path(path)))

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import SchedPlus tasks", "", "JSON (*.json)"
        )
        if not path:
            return
        try:
            result = import_tasks(Path(path))
            self.scheduler.load_tasks()
            self.refresh_views()
            QMessageBox.information(
                self,
                "Import complete",
                f"Imported {result.imported}; skipped {result.duplicates} duplicate(s) "
                f"and {result.conflicts} conflict(s).",
            )
        except (DataTransferError, StorageError) as exc:
            QMessageBox.critical(self, "Unable to import tasks", str(exc))

    def _run_data_action(self, success_message, operation):
        try:
            operation()
            self.show_status_message(success_message)
        except (DataTransferError, StorageError) as exc:
            QMessageBox.critical(self, "Data operation failed", str(exc))

    def show_shortcuts(self):
        shortcuts = (
            "Ctrl+N — New task\n"
            "Ctrl+E — Edit selected task\n"
            "Delete — Delete selected task\n"
            "Ctrl+Z — Undo last action\n"
            "Ctrl+F — Search tasks\n"
            "Ctrl+R — Reload tasks\n"
            "Ctrl+Q — Quit\n"
            "Ctrl+, — Settings\n"
            "F11 — Toggle full screen\n"
            "Esc — Close dialog"
        )
        QMessageBox.information(self, "Keyboard shortcuts", shortcuts)

    def show_about(self):
        build = self.identity
        about_text = (
            f"<h3>SchedPlus</h3>"
            f"<p>{build.details}</p>"
            f"<p>A local-first desktop task scheduler.</p>"
            f"<p>All data is stored on your device. "
            f"No accounts, no sync, no external services.</p>"
            f"<p>Open source under the Apache 2.0 license.</p>"
        )
        QMessageBox.about(self, "About SchedPlus", about_text)

    def check_for_updates(self):
        self.show_status_message("Checking for updates…")
        self.update_thread = start_update_check(
            self.update_signals.ready.emit, self.update_signals.failed.emit
        )

    def show_update_status(self):
        try:
            state = read_state()
            details = f"Status: {state.status}"
            if state.target_version:
                details += f"\nTarget version: {state.target_version}"
            if state.message:
                details += f"\n{state.message}"
        except UpdateError as exc:
            details = str(exc)
        QMessageBox.information(self, "Last update result", details)

    def _offer_prepared_update(self, build_info, prepared):
        prompt = QMessageBox(self)
        prompt.setIcon(QMessageBox.Icon.Information)
        prompt.setWindowTitle("SchedPlus update ready")
        prompt.setText(
            f"SchedPlus {prepared.check.latest_version} is ready to install."
        )
        if prepared.action == "download":
            prompt.setInformativeText(
                "The verified package has been downloaded. Open its folder to install it with your package tools."
            )
        else:
            prompt.setInformativeText(
                "SchedPlus will close after handing off the verified update."
            )
        prompt.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        prompt.button(QMessageBox.StandardButton.Yes).setText(
            "Open download" if prepared.action == "download" else "Close and update"
        )
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
        if prepared.action != "download":
            QApplication.instance().quit()

    def toggle_full_screen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def undo_last_action(self):
        result = self.scheduler.undo_manager.undo()
        if result:
            self.refresh_views()
            self.show_status_message(result)
        else:
            self.show_status_message("Nothing to undo")

    def reschedule_task(self, task, date, time):
        self.scheduler.undo_manager.record_edit(task)
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
