"""Kanban board view for planning tasks."""

from PyQt6.QtCore import QMimeData, Qt, pyqtSignal
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from logic.board import BOARD_STAGES, group_by_stage

BOARD_STAGE_LABELS = {
    "backlog": "Backlog",
    "in_progress": "In progress",
    "done": "Done",
}

BOARD_MIME_TYPE = "application/x-schedplus-task"


class BoardCard(QWidget):
    """A single task card rendered on the board."""

    edit_requested = pyqtSignal(object)
    delete_requested = pyqtSignal(object)
    complete_requested = pyqtSignal(object)

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self._column = None
        self.setObjectName("BoardCard")
        self.setToolTip(
            "Drag to a column to move it; double-click to edit. "
            "Arrow keys move between cards."
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(f"Task: {task.text}")
        self.setAccessibleDescription(
            BOARD_STAGE_LABELS.get(task.board_stage, "Not on board")
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        if task.completed == "true":
            done_badge = QLabel("Done")
            done_badge.setObjectName("CategoryBadge")
            layout.addWidget(done_badge, alignment=Qt.AlignmentFlag.AlignLeft)

        text = QLabel(task.text)
        text.setObjectName("CardText")
        text.setWordWrap(True)
        layout.addWidget(text)

        schedule = QLabel(f"{task.date} {task.time}".strip())
        schedule.setObjectName("MutedLabel")
        layout.addWidget(schedule)

        meta = QHBoxLayout()
        meta.setSpacing(6)
        if task.category:
            category = QLabel(task.category)
            category.setObjectName("CategoryBadge")
            meta.addWidget(category)
        if task.priority == "high":
            priority = QLabel("High priority")
            priority.setObjectName("PriorityHigh")
            meta.addWidget(priority)
        for value, label in (("duration", "min"), ("recurrence", "")):
            stored = getattr(task, value) or ""
            if not stored:
                continue
            hint = QLabel(f"{stored}{label}" if label else stored)
            hint.setObjectName("MutedLabel")
            meta.addWidget(hint)
        if task.reminder:
            reminder = QLabel(f"-{task.reminder} min")
            reminder.setObjectName("MutedLabel")
            meta.addWidget(reminder)
        meta.addStretch()
        if meta.count() > 1:
            layout.addLayout(meta)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        self.complete_button = QPushButton(
            "Uncomplete" if task.completed == "true" else "Complete"
        )
        self.complete_button.setObjectName("SecondaryButton")
        self.complete_button.setAccessibleName(
            "Mark task incomplete" if task.completed == "true" else "Complete task"
        )
        self.edit_button = QPushButton("Edit")
        self.edit_button.setObjectName("SecondaryButton")
        self.edit_button.setAccessibleName("Edit task")
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("DangerButton")
        self.delete_button.setAccessibleName("Delete task")
        actions.addWidget(self.complete_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        layout.addLayout(actions)

        self.complete_button.clicked.connect(lambda: self.complete_requested.emit(task))
        self.edit_button.clicked.connect(lambda: self.edit_requested.emit(task))
        self.delete_button.clicked.connect(lambda: self.delete_requested.emit(task))

    @staticmethod
    def drag_mime(task) -> QMimeData:
        mime = QMimeData()
        mime.setData(BOARD_MIME_TYPE, task.id.encode("utf-8"))
        return mime

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            drag.setMimeData(self.drag_mime(self.task))
            drag.setPixmap(self.grab())
            drag.setHotSpot(drag.pixmap().rect().center())
            drag.exec(Qt.DropAction.MoveAction)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.edit_requested.emit(self.task)
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        board = self._column.board if self._column is not None else None
        if key == Qt.Key.Key_Left:
            if board is not None:
                board.move_focus(self, column_delta=-1)
            event.accept()
        elif key == Qt.Key.Key_Right:
            if board is not None:
                board.move_focus(self, column_delta=1)
            event.accept()
        elif key == Qt.Key.Key_Up:
            if board is not None:
                board.move_focus(self, row_delta=-1)
            event.accept()
        elif key == Qt.Key.Key_Down:
            if board is not None:
                board.move_focus(self, row_delta=1)
            event.accept()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.edit_requested.emit(self.task)
            event.accept()
        elif key == Qt.Key.Key_Delete:
            self.delete_requested.emit(self.task)
            event.accept()
        else:
            super().keyPressEvent(event)


class BoardColumn(QWidget):
    """A single stage column holding task cards."""

    edit_requested = pyqtSignal(object)
    delete_requested = pyqtSignal(object)
    complete_requested = pyqtSignal(object)
    move_requested = pyqtSignal(str, str)

    def __init__(self, stage: str, parent=None):
        super().__init__(parent)
        self.stage = stage
        self.board = None
        self.setObjectName("BoardColumn")
        self.setAcceptDrops(True)
        self.setToolTip("Drop a card here to move it")

        title = BOARD_STAGE_LABELS[stage]
        self.setAccessibleName(title)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("BoardColumnTitle")
        self.title_label.setAccessibleName(title)
        layout.addWidget(self.title_label)

        self.empty_label = QLabel("No tasks")
        self.empty_label.setObjectName("MutedLabel")
        layout.addWidget(self.empty_label)

        self.cards = QWidget()
        self.card_layout = QVBoxLayout(self.cards)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(8)
        self.card_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.cards)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setAccessibleName(title)
        layout.addWidget(scroll, 1)

    def set_tasks(self, tasks):
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
        self.card_layout.addStretch()
        for task in tasks:
            card = BoardCard(task)
            card._column = self
            card.edit_requested.connect(self.edit_requested)
            card.delete_requested.connect(self.delete_requested)
            card.complete_requested.connect(self.complete_requested)
            self.card_layout.insertWidget(self.card_layout.count() - 1, card)
        self.empty_label.setVisible(len(tasks) == 0)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(BOARD_MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(BOARD_MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime = event.mimeData()
        if not mime.hasFormat(BOARD_MIME_TYPE):
            event.ignore()
            return
        task_id = bytes(mime.data(BOARD_MIME_TYPE)).decode("utf-8")
        self.move_requested.emit(task_id, self.stage)
        event.acceptProposedAction()


class BoardView(QWidget):
    """Kanban planning board: one column per stage."""

    add_requested = pyqtSignal()
    edit_requested = pyqtSignal(object)
    delete_requested = pyqtSignal(object)
    complete_requested = pyqtSignal(object)
    move_requested = pyqtSignal(object, str)

    def __init__(self, scheduler, parent=None):
        super().__init__(parent)
        self.scheduler = scheduler

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        heading_row = QHBoxLayout()
        heading = QLabel("Kanban")
        heading.setObjectName("PageHeading")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search cards…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setAccessibleName("Search Kanban cards")
        self.search_input.setMaximumWidth(230)
        self.count_label = QLabel()
        self.count_label.setObjectName("MutedLabel")
        self.add_button = QPushButton("＋ Add task")
        self.add_button.setObjectName("PrimaryButton")
        self.add_button.setAccessibleName("Add new task")
        heading_row.addWidget(heading)
        heading_row.addStretch()
        heading_row.addWidget(self.search_input)
        heading_row.addWidget(self.count_label)
        heading_row.addWidget(self.add_button)
        layout.addLayout(heading_row)

        self.columns_widget = QWidget()
        self.columns_row = QHBoxLayout(self.columns_widget)
        self.columns_row.setContentsMargins(0, 0, 0, 0)
        self.columns_row.setSpacing(14)
        self.columns: dict[str, BoardColumn] = {}
        for stage in BOARD_STAGES:
            column = BoardColumn(stage)
            column.board = self
            column.edit_requested.connect(self.edit_requested)
            column.delete_requested.connect(self.delete_requested)
            column.complete_requested.connect(self.complete_requested)
            column.move_requested.connect(self._resolve_move)
            self.columns[stage] = column
            self.columns_row.addWidget(column, 1)
        layout.addWidget(self.columns_widget, 1)

        self.empty_label = QLabel()
        self.empty_label.setObjectName("EmptyState")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setMinimumHeight(180)
        layout.addWidget(self.empty_label, 1)

        self.add_button.clicked.connect(self.add_requested)
        self.search_input.textChanged.connect(self._apply_search)
        self.search_text = ""
        self.refresh()

    def refresh(self):
        all_tasks = self.scheduler.get_tasks()
        query = self.search_text
        visible = [
            task for task in all_tasks if not query or query in task.text.casefold()
        ]
        grouped = group_by_stage(visible)
        on_board = sum(len(tasks) for tasks in grouped.values())
        for stage, column in self.columns.items():
            column.set_tasks(grouped[stage])
        self.columns_widget.setVisible(on_board > 0)
        self.empty_label.setVisible(on_board == 0)
        if query and on_board == 0 and any(bool(t.board_stage) for t in all_tasks):
            self.empty_label.setText("No cards match the search.")
        else:
            self.empty_label.setText(
                "No tasks on the board.\n"
                "Add a task and tick \u201cAdd to Kanban\u201d to start planning."
            )
        self.count_label.setText(f"{on_board} of {len(all_tasks)} tasks on the board")

    def _apply_search(self, text: str):
        self.search_text = text.strip().casefold()
        self.refresh()

    def _cards(self, stage: str) -> list[BoardCard]:
        layout = self.columns[stage].card_layout
        cards: list[BoardCard] = []
        for index in range(layout.count()):
            item = layout.itemAt(index)
            if item is None:
                continue
            widget = item.widget()
            if isinstance(widget, BoardCard):
                cards.append(widget)
        return cards

    def _nav_target(
        self, card: BoardCard, column_delta=0, row_delta=0
    ) -> BoardCard | None:
        stages = list(BOARD_STAGES)
        columns = {stage: self._cards(stage) for stage in stages}
        current_col = next(
            (index for index, stage in enumerate(stages) if card in columns[stage]),
            None,
        )
        if current_col is None or not columns[stages[current_col]]:
            return None
        current_row = columns[stages[current_col]].index(card)
        target_col = max(0, min(len(stages) - 1, current_col + column_delta))
        target_cards = columns[stages[target_col]]
        if not target_cards:
            return None
        if column_delta:
            target_row = min(current_row, len(target_cards) - 1)
        else:
            target_row = max(0, min(len(target_cards) - 1, current_row + row_delta))
        return target_cards[target_row]

    def move_focus(self, card: BoardCard, column_delta=0, row_delta=0):
        target = self._nav_target(card, column_delta, row_delta)
        if target is not None:
            target.setFocus()

    def _resolve_move(self, task_id: str, stage: str):
        for task in self.scheduler.get_tasks():
            if task.id == task_id:
                self.move_requested.emit(task, stage)
                return

    def focus_add(self):
        self.add_button.setFocus()
