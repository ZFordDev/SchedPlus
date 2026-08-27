"""Native month, week, and day scheduling workspace."""

from collections import Counter, defaultdict
from datetime import datetime

from PyQt6.QtCore import QDate, QPoint, QTime, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCalendarWidget,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.pyqt.settings_dialog import UiPreferences


TASK_ROLE = int(Qt.ItemDataRole.UserRole)


class EventCalendar(QCalendarWidget):
    """Month calendar that marks dates containing scheduled tasks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_counts = Counter()
        self.setGridVisible(False)
        self.setNavigationBarVisible(False)

    def set_tasks(self, tasks):
        self.task_counts = Counter(task.date for task in tasks)
        self.updateCells()

    def paintCell(self, painter: QPainter, rect, calendar_date: QDate):
        super().paintCell(painter, rect, calendar_date)
        count = self.task_counts.get(calendar_date.toString("yyyy-MM-dd"), 0)
        if not count:
            return
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#2563EB"))
        radius = 3
        center = QPoint(rect.center().x(), rect.bottom() - 6)
        painter.drawEllipse(center, radius, radius)
        painter.restore()


class ScheduleTable(QTableWidget):
    """Timed grid that emits semantic add, edit, delete, and move requests."""

    add_requested = pyqtSignal(str, str)
    edit_requested = pyqtSignal(object)
    delete_requested = pyqtSignal(object)
    task_dropped = pyqtSignal(object, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slot_dates = []
        self.slot_times = []
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.cellDoubleClicked.connect(self._activate_cell)

    def configure(self, dates: list[str], times: list[str]):
        self.clear()
        self.slot_dates = dates
        self.slot_times = times
        self.setRowCount(len(times))
        self.setColumnCount(len(dates))
        self.setHorizontalHeaderLabels(
            [
                QDate.fromString(value, "yyyy-MM-dd").toString("ddd\nd MMM")
                for value in dates
            ]
        )
        self.setVerticalHeaderLabels(times)
        self.horizontalHeader().setSectionResizeMode(
            self.horizontalHeader().ResizeMode.Stretch
        )
        for row in range(len(times)):
            self.setRowHeight(row, 38)

    def render_tasks(self, tasks):
        grouped = defaultdict(list)
        for task in tasks:
            if task.date not in self.slot_dates:
                continue
            row = self._row_for_time(task.time)
            if row is not None:
                grouped[(row, self.slot_dates.index(task.date))].append(task)

        for (row, column), cell_tasks in grouped.items():
            first = cell_tasks[0]
            suffix = f"  +{len(cell_tasks) - 1}" if len(cell_tasks) > 1 else ""
            item = QTableWidgetItem(f"{first.time}  {first.text}{suffix}")
            item.setData(TASK_ROLE, first)
            item.setToolTip(
                "\n".join(f"{task.time}  {task.text}" for task in cell_tasks)
            )
            item.setBackground(QColor("#DBEAFE"))
            item.setForeground(QColor("#172033"))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)
            self.setItem(row, column, item)

    def selected_task(self):
        item = self.currentItem()
        return item.data(TASK_ROLE) if item else None

    def dropEvent(self, event):
        item = self.currentItem()
        task = item.data(TASK_ROLE) if item else None
        target = self.indexAt(event.position().toPoint())
        if task and target.isValid():
            self.task_dropped.emit(
                task,
                self.slot_dates[target.column()],
                self.slot_times[target.row()],
            )
            event.acceptProposedAction()
            return
        event.ignore()

    def _row_for_time(self, value):
        try:
            parsed = datetime.strptime(value, "%H:%M")
        except ValueError:
            return None
        minutes = parsed.hour * 60 + parsed.minute
        slots = [int(time[:2]) * 60 + int(time[3:]) for time in self.slot_times]
        if not slots or minutes < slots[0] or minutes > slots[-1] + 29:
            return None
        return min(range(len(slots)), key=lambda index: abs(slots[index] - minutes))

    def _activate_cell(self, row, column):
        item = self.item(row, column)
        task = item.data(TASK_ROLE) if item else None
        if task:
            self.edit_requested.emit(task)
        else:
            self.add_requested.emit(self.slot_dates[column], self.slot_times[row])


class CalendarWorkspace(QWidget):
    add_requested = pyqtSignal(str, str)
    edit_requested = pyqtSignal(object)
    delete_requested = pyqtSignal(object)
    reschedule_requested = pyqtSignal(object, str, str)

    def __init__(self, scheduler, preferences: UiPreferences, parent=None):
        super().__init__(parent)
        self.scheduler = scheduler
        self.preferences = preferences

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Calendar")
        title.setObjectName("PageHeading")
        self.previous_button = QPushButton("‹")
        self.today_button = QPushButton("Today")
        self.next_button = QPushButton("›")
        self.view_combo = QComboBox()
        self.view_combo.addItem("Month", "month")
        self.view_combo.addItem("Week", "week")
        self.view_combo.addItem("Day", "day")
        self.period_label = QLabel()
        self.period_label.setObjectName("MutedLabel")
        header.addWidget(title)
        header.addSpacing(18)
        header.addWidget(self.previous_button)
        header.addWidget(self.today_button)
        header.addWidget(self.next_button)
        header.addWidget(self.period_label)
        header.addStretch()
        header.addWidget(self.view_combo)
        layout.addLayout(header)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_month_page())
        self.week_table = ScheduleTable()
        self.day_table = ScheduleTable()
        self.pages.addWidget(self.week_table)
        self.pages.addWidget(self.day_table)
        layout.addWidget(self.pages, 1)

        actions = QHBoxLayout()
        self.add_button = QPushButton("＋ Add task")
        self.add_button.setObjectName("PrimaryButton")
        self.edit_button = QPushButton("Edit selected")
        self.edit_button.setObjectName("SecondaryButton")
        self.delete_button = QPushButton("Delete selected")
        self.delete_button.setObjectName("DangerButton")
        actions.addWidget(self.add_button)
        actions.addStretch()
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        layout.addLayout(actions)

        self.previous_button.clicked.connect(lambda: self.navigate(-1))
        self.next_button.clicked.connect(lambda: self.navigate(1))
        self.today_button.clicked.connect(self.go_to_today)
        self.view_combo.currentIndexChanged.connect(self._change_view)
        self.month_calendar.selectionChanged.connect(self.refresh)
        self.month_agenda.itemDoubleClicked.connect(self._edit_agenda_item)
        self.month_agenda.itemSelectionChanged.connect(self._update_actions)
        self.week_table.itemSelectionChanged.connect(self._update_actions)
        self.day_table.itemSelectionChanged.connect(self._update_actions)
        self.add_button.clicked.connect(self._add_for_selection)
        self.edit_button.clicked.connect(self._edit_selected)
        self.delete_button.clicked.connect(self._delete_selected)

        for table in (self.week_table, self.day_table):
            table.add_requested.connect(self.add_requested)
            table.edit_requested.connect(self.edit_requested)
            table.delete_requested.connect(self.delete_requested)
            table.task_dropped.connect(self.reschedule_requested)

        self.apply_preferences(preferences)
        self.refresh()

    def _build_month_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter()
        self.month_calendar = EventCalendar()
        agenda_panel = QWidget()
        agenda_layout = QVBoxLayout(agenda_panel)
        agenda_layout.setContentsMargins(10, 0, 0, 0)
        agenda_layout.setSpacing(8)
        self.month_agenda_heading = QLabel()
        self.month_agenda_heading.setObjectName("SectionHeading")
        self.month_agenda = QListWidget()
        self.month_agenda.setAlternatingRowColors(True)
        self.month_agenda.setSpacing(2)
        self.month_empty = QLabel("No tasks scheduled for this date.")
        self.month_empty.setObjectName("EmptyState")
        self.month_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_empty.setWordWrap(True)
        agenda_layout.addWidget(self.month_agenda_heading)
        agenda_layout.addWidget(self.month_agenda, 1)
        agenda_layout.addWidget(self.month_empty, 1)
        splitter.addWidget(self.month_calendar)
        splitter.addWidget(agenda_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        return page

    def apply_preferences(self, preferences: UiPreferences):
        self.preferences = preferences
        first_day = (
            Qt.DayOfWeek.Monday
            if preferences.first_day_of_week == "monday"
            else Qt.DayOfWeek.Sunday
        )
        self.month_calendar.setFirstDayOfWeek(first_day)
        if preferences.show_week_numbers:
            self.month_calendar.setVerticalHeaderFormat(
                QCalendarWidget.VerticalHeaderFormat.ISOWeekNumbers
            )
        else:
            self.month_calendar.setVerticalHeaderFormat(
                QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
            )
        index = self.view_combo.findData(preferences.calendar_view)
        self.view_combo.setCurrentIndex(max(0, index))
        self.refresh()

    def current_view(self):
        return self.view_combo.currentData()

    def refresh(self):
        tasks = self.scheduler.get_tasks()
        selected = self.month_calendar.selectedDate()
        self.month_calendar.set_tasks(tasks)
        self._render_month_agenda(tasks, selected)
        self._render_week(tasks, selected)
        self._render_day(tasks, selected)
        self._update_period_label(selected)
        self._update_actions()

    def navigate(self, amount):
        selected = self.month_calendar.selectedDate()
        if self.current_view() == "month":
            selected = selected.addMonths(amount)
        elif self.current_view() == "week":
            selected = selected.addDays(amount * 7)
        else:
            selected = selected.addDays(amount)
        self.month_calendar.setSelectedDate(selected)
        self.month_calendar.setCurrentPage(selected.year(), selected.month())
        self.refresh()

    def go_to_today(self):
        today = QDate.currentDate()
        self.month_calendar.setSelectedDate(today)
        self.month_calendar.setCurrentPage(today.year(), today.month())
        self.refresh()

    def selected_task(self):
        if self.current_view() == "month":
            item = self.month_agenda.currentItem()
            return item.data(TASK_ROLE) if item else None
        table = self.week_table if self.current_view() == "week" else self.day_table
        return table.selected_task()

    def _render_month_agenda(self, tasks, selected):
        selected_value = selected.toString("yyyy-MM-dd")
        self.month_agenda_heading.setText(selected.toString("dddd, d MMMM"))
        self.month_agenda.clear()
        for task in sorted(
            (task for task in tasks if task.date == selected_value),
            key=lambda task: (task.time, task.text.casefold()),
        ):
            item = QListWidgetItem(f"{task.time}   {task.text}")
            item.setData(TASK_ROLE, task)
            self.month_agenda.addItem(item)
        has_tasks = self.month_agenda.count() > 0
        self.month_agenda.setVisible(has_tasks)
        self.month_empty.setVisible(not has_tasks)

    def _render_week(self, tasks, selected):
        offset = (
            selected.dayOfWeek() - 1
            if self.preferences.first_day_of_week == "monday"
            else selected.dayOfWeek() % 7
        )
        start = selected.addDays(-offset)
        dates = [start.addDays(day).toString("yyyy-MM-dd") for day in range(7)]
        relevant = [task for task in tasks if task.date in dates]
        times = self._time_slots(relevant)
        self.week_table.configure(dates, times)
        self.week_table.render_tasks(tasks)

    def _render_day(self, tasks, selected):
        dates = [selected.toString("yyyy-MM-dd")]
        relevant = [task for task in tasks if task.date in dates]
        self.day_table.configure(dates, self._time_slots(relevant))
        self.day_table.render_tasks(tasks)

    def _time_slots(self, tasks):
        start = self.preferences.workday_start * 2
        end = self.preferences.workday_end * 2
        for task in tasks:
            try:
                hour, minute = (int(part) for part in task.time.split(":"))
            except (AttributeError, TypeError, ValueError):
                continue
            task_slot = hour * 2 + (1 if minute >= 30 else 0)
            start = min(start, task_slot)
            end = max(end, task_slot)
        return [
            f"{slot // 2:02d}:{(slot % 2) * 30:02d}" for slot in range(start, end + 1)
        ]

    def _update_period_label(self, selected):
        if self.current_view() == "month":
            text = selected.toString("MMMM yyyy")
        elif self.current_view() == "week":
            start = self.week_table.slot_dates[0]
            end = self.week_table.slot_dates[-1]
            text = f"{start} — {end}"
        else:
            text = selected.toString("dddd, d MMMM yyyy")
        self.period_label.setText(text)

    def _change_view(self):
        self.pages.setCurrentIndex(self.view_combo.currentIndex())
        self.refresh()

    def _add_for_selection(self):
        selected = self.month_calendar.selectedDate().toString("yyyy-MM-dd")
        time = QTime.currentTime().toString("HH:mm")
        self.add_requested.emit(selected, time)

    def _edit_agenda_item(self, item):
        task = item.data(TASK_ROLE)
        if task:
            self.edit_requested.emit(task)

    def _edit_selected(self):
        task = self.selected_task()
        if task:
            self.edit_requested.emit(task)

    def _delete_selected(self):
        task = self.selected_task()
        if task:
            self.delete_requested.emit(task)

    def _update_actions(self):
        selected = self.selected_task() is not None
        self.edit_button.setEnabled(selected)
        self.delete_button.setEnabled(selected)
