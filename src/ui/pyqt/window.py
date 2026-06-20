# src/ui/pyqt/window.py

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStatusBar
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor

from ui.pyqt.task_list import TaskListWidget
from ui.pyqt.add_dialog import AddTaskDialog


class SchedPlusWindow(QMainWindow):
    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler

        self.setWindowTitle("SchedPlus")
        self.resize(520, 680) # Slightly taller for better task distribution
        self.setStyleSheet("background-color: #FAFAFA;") # Soft global background

        # Status Bar Styling
        status = self.statusBar()
        status.setStyleSheet("""
            QStatusBar {
                background: #F0F0F0;
                color: #555555;
                font-size: 11px;
                border-top: 1px solid #E0E0E0;
            }
            QStatusBar::item { border: none; }
        """)
        
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.clear_status_message)

        # Central Layout Setup
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) # Tighten the gap between header and content

        # ---------------------------------------------------------
        # HEADER BAR
        # ---------------------------------------------------------
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-bottom: 1px solid #EAEAEA;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 16, 20, 16)

        title = QLabel("SchedPlus")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1A1A1A;
                border: none;
            }
        """)

        # Cleaned up header button to match the app style
        self.add_btn = QPushButton("＋ Add Task")
        self.add_btn.setFixedHeight(34)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #007ACC;
                color: white;
                border-radius: 6px;
                padding: 0px 16px;
                font-weight: bold;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover { background: #0062A3; }
            QPushButton:pressed { background: #004C80; }
        """)
        self.add_btn.clicked.connect(self.open_add_dialog)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)

        layout.addWidget(header_widget)

        # ---------------------------------------------------------
        # TASK LIST
        # ---------------------------------------------------------
        self.task_list = TaskListWidget(scheduler)
        layout.addWidget(self.task_list)

        # CONNECT THE TASK LIST BUTTON:
        # We hook the task list's internal add button directly to this controller method
        self.task_list.add_button.clicked.connect(self.open_add_dialog)

        self.setCentralWidget(central)
        self.show_status_message("Tasks loaded")

    def open_add_dialog(self):
        dialog = AddTaskDialog()
        if dialog.exec():
            # Destructuring layout values safely
            result = dialog.get_values()
            if len(result) == 3:
                date, time, text = result
                if date and time and text:
                    self.scheduler.add_task(date, time, text)
                    self.task_list.refresh()
                    self.show_status_message("Task added successfully")

    def show_status_message(self, msg, duration=3000):
        self.statusBar().showMessage(f"  {msg}") # Tiny padding spacer
        self.status_timer.start(duration)

    def clear_status_message(self):
        self.statusBar().clearMessage()