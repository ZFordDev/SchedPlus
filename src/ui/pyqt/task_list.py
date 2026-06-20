# src/ui/pyqt/task_list.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from ui.pyqt.task_card import TaskCard


class TaskListWidget(QWidget):
    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Scroll Area Setup
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Remove default harsh QScrollArea border
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Scroll Content Container
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(12)
        self.container_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self.container)
        layout.addWidget(scroll)

        # Add Button (Styled & separated)
        self.add_button = QPushButton("＋ Add Task")
        self.add_button.setFixedHeight(42)
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0062A3;
            }
            QPushButton:pressed {
                background-color: #004C80;
            }
        """)
        layout.addWidget(self.add_button)

        self.refresh()

    # ---------------------------------------------------------
    # RENDER & CLEANUP
    # ---------------------------------------------------------

    def _clear_layout(self):
        """Safely clears all widgets, layouts, and spacers from the container."""
        while self.container_layout.count() > 0:
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh(self):
        self._clear_layout()

        tasks = self.scheduler.get_tasks()

        # Dynamic Auto-Hide UI Logic
        if not tasks:
            self._render_empty_state()
            self.add_button.show()  # Bring back the button if the list becomes empty
            return

        self.add_button.hide()  # Auto-hide the button to avoid duplication with the header

        # Sort and group tasks by date
        grouped = {}
        for t in sorted(tasks, key=lambda x: x.date):
            grouped.setdefault(t.date, []).append(t)

        # Render groups
        for date, items in grouped.items():
            self._render_date_header(date)

            for task in items:
                card = TaskCard(task)
                self.container_layout.addWidget(card)

        # Push everything to the top safely
        self.container_layout.addStretch(1)

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def _render_date_header(self, date):
        # Header container to hold label and line together neatly
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 8, 0, 4)
        header_layout.setSpacing(4)

        label = QLabel(date)
        label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #555555;
            }
        """)
        header_layout.addWidget(label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("border: none; background-color: #E0E0E0; max-height: 1px;")
        header_layout.addWidget(line)

        self.container_layout.addWidget(header_widget)

    def _render_empty_state(self):
        label = QLabel("No tasks yet.\nClick 'Add Task' to create one.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #888888;
                line-height: 1.4;
                padding: 60px 20px;
            }
        """)
        self.container_layout.addWidget(label)