# src/ui/pyqt/add_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QDateEdit, QTimeEdit, QLabel
)
from PyQt6.QtCore import QDate, QTime, Qt


class AddTaskDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create New Task")
        self.setFixedSize(400, 360)
        
        # Make the dialog background match a crisp, clean modal style
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #555555;
                margin-bottom: 2px;
            }
            QLineEdit, QDateEdit, QTimeEdit {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #1A1A1A;
            }
            QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus {
                border: 1px solid #007ACC;
                background-color: #FFFFFF;
            }
            /* Clean up the native dropdown arrow for date picker */
            QDateEdit::drop-down, QTimeEdit::up-button, QTimeEdit::down-button {
                border: none;
                background: transparent;
            }
        """)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # --- Task Input Field ---
        task_block = QVBoxLayout()
        task_block.setSpacing(4)
        task_label = QLabel("WHAT NEEDS TO BE DONE?")
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("e.g., Review project proposal")
        task_block.addWidget(task_label)
        task_block.addWidget(self.text_input)
        main_layout.addLayout(task_block)

        # --- Date & Time Fields (Side by Side) ---
        dt_layout = QHBoxLayout()
        dt_layout.setSpacing(16)

        # Date Field
        date_block = QVBoxLayout()
        date_block.setSpacing(4)
        date_label = QLabel("DATE")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDate(QDate.currentDate())
        date_block.addWidget(date_label)
        date_block.addWidget(self.date_input)
        dt_layout.addLayout(date_block)

        # Time Field
        time_block = QVBoxLayout()
        time_block.setSpacing(4)
        time_label = QLabel("TIME")
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        self.time_input.setTime(QTime.currentTime())
        time_block.addWidget(time_label)
        time_block.addWidget(self.time_input)
        dt_layout.addLayout(time_block)

        main_layout.addLayout(dt_layout)

        # Spacer to push layout cleanly
        main_layout.addStretch()

        # ---------------------------------------------------------
        # CUSTOM ACTION BUTTONS
        # ---------------------------------------------------------
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(38)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0F0F0;
                color: #444444;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover { background-color: #E5E5E5; }
        """)
        
        self.save_btn = QPushButton("Save Task")
        self.save_btn.setFixedHeight(38)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover { background-color: #0062A3; }
            QPushButton:pressed { background-color: #004C80; }
        """)

        # Connect slots
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.accept)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(button_layout)

    def get_values(self):
        date_str = self.date_input.date().toString("yyyy-MM-dd")
        time_str = self.time_input.time().toString("HH:mm")
        text_str = self.text_input.text().strip()

        return date_str, time_str, text_str