"""Model-backed task table with search, filtering, and sorting."""

from datetime import date

from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    pyqtSignal,
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from ui.pyqt.settings_dialog import FILTERS, SORT_FIELDS, UiPreferences


class TaskTableModel(QAbstractTableModel):
    HEADERS = ("Date", "Time", "Task", "Status", "Created")

    def __init__(
        self, tasks=None, parent=None, date_format="yyyy-MM-dd", time_format="HH:mm"
    ):
        super().__init__(parent)
        self.tasks = list(tasks or [])
        self.date_format = date_format
        self.time_format = time_format

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.tasks)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        task = self.tasks[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 3:
                return "Done" if task.completed == "true" else ""
            return (task.date, task.time, task.text, "", task.createdAt)[index.column()]
        if role == Qt.ItemDataRole.UserRole:
            return task
        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() in (0, 1, 3):
            return Qt.AlignmentFlag.AlignCenter
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.HEADERS[section]
        return None

    def replace_tasks(self, tasks):
        self.beginResetModel()
        self.tasks = list(tasks)
        self.endResetModel()


class TaskFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text = ""
        self.task_filter = "all"
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def set_search_text(self, text: str):
        self.search_text = text.strip().casefold()
        self.invalidateFilter()

    def set_task_filter(self, task_filter: str):
        self.task_filter = task_filter
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        task = model.tasks[source_row]
        if self.search_text and self.search_text not in task.text.casefold():
            return False

        is_completed = task.completed == "true"
        today = date.today().isoformat()

        if self.task_filter == "completed":
            return is_completed
        if self.task_filter == "active":
            return not is_completed
        if self.task_filter == "today":
            return task.date == today and not is_completed
        if self.task_filter == "upcoming":
            return task.date >= today and not is_completed
        return True


class TaskListWidget(QWidget):
    add_requested = pyqtSignal()
    edit_requested = pyqtSignal(object)
    delete_requested = pyqtSignal(object)
    complete_requested = pyqtSignal(object)

    SORT_COLUMNS = {"date": 0, "time": 1, "text": 2, "status": 3, "created": 4}

    def __init__(self, scheduler, preferences: UiPreferences, parent=None):
        super().__init__(parent)
        self.scheduler = scheduler

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        heading_row = QHBoxLayout()
        heading = QLabel("Tasks")
        heading.setObjectName("PageHeading")
        self.count_label = QLabel()
        self.count_label.setObjectName("MutedLabel")
        heading_row.addWidget(heading)
        heading_row.addStretch()
        heading_row.addWidget(self.count_label)
        layout.addLayout(heading_row)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setAccessibleName("Search tasks")

        self.filter_combo = QComboBox()
        for value, label in FILTERS.items():
            self.filter_combo.addItem(label, value)
        self.filter_combo.setAccessibleName("Task filter")

        self.sort_combo = QComboBox()
        for value, label in SORT_FIELDS.items():
            self.sort_combo.addItem(f"Sort: {label}", value)
        self.sort_combo.setAccessibleName("Sort field")

        self.order_button = QPushButton("Ascending")
        self.order_button.setCheckable(True)
        self.order_button.setObjectName("SecondaryButton")
        self.order_button.setAccessibleName("Sort order")

        controls.addWidget(self.search_input, 1)
        controls.addWidget(self.filter_combo)
        controls.addWidget(self.sort_combo)
        controls.addWidget(self.order_button)
        layout.addLayout(controls)

        self.model = TaskTableModel(
            scheduler.get_tasks(),
            self,
            preferences.date_format,
            preferences.time_format,
        )
        self.proxy = TaskFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)

        self.empty_label = QLabel()
        self.empty_label.setObjectName("MutedLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setMinimumHeight(180)
        layout.addWidget(self.empty_label, 1)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(2, 460)
        self.table.horizontalHeader().setSectionResizeMode(
            2, self.table.horizontalHeader().ResizeMode.Stretch
        )
        self.table.doubleClicked.connect(self._emit_edit)
        self.table.setAccessibleName("Task list")
        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        self.add_button = QPushButton("＋ Add task")
        self.add_button.setObjectName("PrimaryButton")
        self.add_button.setAccessibleName("Add new task")
        self.edit_button = QPushButton("Edit")
        self.edit_button.setObjectName("SecondaryButton")
        self.edit_button.setAccessibleName("Edit selected task")
        self.complete_button = QPushButton("Complete")
        self.complete_button.setObjectName("SecondaryButton")
        self.complete_button.setAccessibleName("Complete selected task")
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("DangerButton")
        self.delete_button.setAccessibleName("Delete selected task")
        actions.addWidget(self.add_button)
        actions.addStretch()
        actions.addWidget(self.edit_button)
        actions.addWidget(self.complete_button)
        actions.addWidget(self.delete_button)
        layout.addLayout(actions)

        self.search_input.textChanged.connect(self._apply_search)
        self.filter_combo.currentIndexChanged.connect(self._apply_filter)
        self.sort_combo.currentIndexChanged.connect(self._apply_sort)
        self.order_button.toggled.connect(self._apply_sort)
        self.add_button.clicked.connect(self.add_requested)
        self.edit_button.clicked.connect(self._emit_edit)
        self.complete_button.clicked.connect(self._emit_complete)
        self.delete_button.clicked.connect(self._emit_delete)
        self.table.selectionModel().selectionChanged.connect(self._update_actions)

        self.apply_preferences(preferences)
        self.refresh()

    def apply_preferences(self, preferences: UiPreferences):
        self.model.date_format = preferences.date_format
        self.model.time_format = preferences.time_format
        self.filter_combo.setCurrentIndex(
            max(0, self.filter_combo.findData(preferences.task_filter))
        )
        self.sort_combo.setCurrentIndex(
            max(0, self.sort_combo.findData(preferences.sort_field))
        )
        self.order_button.setChecked(preferences.sort_order == "descending")
        self._apply_filter()
        self._apply_sort()

    def refresh(self):
        self.model.replace_tasks(self.scheduler.get_tasks())
        self._apply_sort()
        visible = self.proxy.rowCount()
        total = len(self.scheduler.get_tasks())
        self.table.setVisible(visible > 0)
        self.empty_label.setVisible(visible == 0)
        self.empty_label.setText(
            "No tasks yet. Add one to start planning."
            if total == 0
            else "No tasks match the current search or filter."
        )
        self.count_label.setText(
            f"{visible} task{'s' if visible != 1 else ''}"
            if visible == total
            else f"{visible} of {total} tasks"
        )
        self._update_actions()

    def selected_task(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        source = self.proxy.mapToSource(rows[0])
        return self.model.tasks[source.row()]

    def focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def current_preferences(self, startup_view="tasks") -> UiPreferences:
        return UiPreferences(
            sort_field=self.sort_combo.currentData(),
            sort_order="descending" if self.order_button.isChecked() else "ascending",
            task_filter=self.filter_combo.currentData(),
            startup_view=startup_view,
        )

    def _apply_filter(self):
        self.proxy.set_task_filter(self.filter_combo.currentData())
        self.refresh_count()

    def _apply_search(self, text):
        self.proxy.set_search_text(text)
        self.refresh_count()

    def _apply_sort(self):
        descending = self.order_button.isChecked()
        self.order_button.setText("Descending" if descending else "Ascending")
        order = (
            Qt.SortOrder.DescendingOrder if descending else Qt.SortOrder.AscendingOrder
        )
        self.proxy.sort(self.SORT_COLUMNS[self.sort_combo.currentData()], order)

    def refresh_count(self):
        visible = self.proxy.rowCount()
        total = len(self.scheduler.get_tasks())
        self.count_label.setText(
            f"{visible} task{'s' if visible != 1 else ''}"
            if visible == total
            else f"{visible} of {total} tasks"
        )

    def _emit_edit(self, _index=None):
        task = self.selected_task()
        if task:
            self.edit_requested.emit(task)

    def _emit_complete(self):
        task = self.selected_task()
        if task:
            self.complete_requested.emit(task)

    def _emit_delete(self):
        task = self.selected_task()
        if task:
            self.delete_requested.emit(task)

    def _update_actions(self, *_args):
        selected = self.selected_task() is not None
        self.edit_button.setEnabled(selected)
        self.complete_button.setEnabled(selected)
        self.delete_button.setEnabled(selected)
        if selected:
            task = self.selected_task()
            self.complete_button.setText(
                "Uncomplete" if task and task.completed == "true" else "Complete"
            )
        else:
            self.complete_button.setText("Complete")
