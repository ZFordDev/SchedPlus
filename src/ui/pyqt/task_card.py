# src/ui/pyqt/task_card.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt


class TaskCard(QWidget):
    def __init__(self, task):
        super().__init__()
        self.task = task

        # Outer layout provides breathing room between individual cards
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 4, 0, 4)
        outer_layout.setSpacing(0)

        # Inner Card Body Container
        self.card_body = QFrame()
        self.card_body.setObjectName("CardBody")
        
        # Inner layout defines padding inside the white card boundary
        inner_layout = QVBoxLayout(self.card_body)
        inner_layout.setContentsMargins(16, 12, 16, 12)
        inner_layout.setSpacing(6)

        # Meta row: Time (Date is removed here because the TaskList already groups by Date Header!)
        meta = QLabel(task.time)
        meta.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: 600;
                color: #007ACC;
                text-transform: uppercase;
            }
        """)

        # Task content (larger, dark off-black, readable line space feel)
        text = QLabel(task.text)
        text.setWordWrap(True)
        text.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #2D3142;
                line-height: 1.3;
            }
        """)

        inner_layout.addWidget(meta)
        inner_layout.addWidget(text)
        
        outer_layout.addWidget(self.card_body)

        # Explicitly styling the ObjectName prevents any inheritance weirdness
        self.setStyleSheet("""
            QFrame#CardBody {
                background: #FFFFFF;
                border: 1px solid #EAEAEA;
                border-radius: 8px;
            }
            QFrame#CardBody:hover {
                border: 1px solid #007ACC;
                background: #FDFDFD;
            }
        """)