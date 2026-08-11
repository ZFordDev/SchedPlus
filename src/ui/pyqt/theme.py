"""Application-wide styling for the advanced native interface."""

BASE_QSS = """
QWidget {
    color: #172033;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 10pt;
}
QMainWindow, QDialog, QWidget#AppRoot {
    background: #F4F6F8;
}
QWidget#Sidebar {
    background: #172033;
}
QLabel#Brand {
    color: white;
    font-size: 18pt;
    font-weight: 700;
}
QLabel#SidebarCaption {
    color: #94A3B8;
    font-size: 9pt;
}
QPushButton#NavigationButton {
    background: transparent;
    color: #CBD5E1;
    border: none;
    border-radius: 6px;
    padding: 10px 12px;
    text-align: left;
}
QPushButton#NavigationButton:hover, QPushButton#NavigationButton:checked {
    background: #273449;
    color: white;
}
QLabel#PageHeading, QLabel#DialogHeading {
    color: #172033;
    font-size: 18pt;
    font-weight: 700;
}
QLabel#MutedLabel {
    color: #657084;
}
QLineEdit, QComboBox, QDateEdit, QTimeEdit {
    background: white;
    border: 1px solid #D8DEE8;
    border-radius: 6px;
    padding: 8px 10px;
    min-height: 18px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
    border-color: #2563EB;
}
QPushButton {
    border-radius: 6px;
    padding: 8px 14px;
}
QPushButton#PrimaryButton, QDialogButtonBox QPushButton[text="Save"] {
    background: #2563EB;
    color: white;
    border: none;
    font-weight: 600;
}
QPushButton#PrimaryButton:hover {
    background: #1D4ED8;
}
QPushButton#SecondaryButton {
    background: white;
    color: #172033;
    border: 1px solid #D8DEE8;
}
QPushButton#SecondaryButton:hover {
    background: #EEF2F7;
}
QPushButton#DangerButton {
    background: #FFF1F2;
    color: #BE123C;
    border: 1px solid #FECDD3;
}
QPushButton:disabled {
    color: #94A3B8;
    background: #E8ECF1;
    border-color: #E8ECF1;
}
QTableView {
    background: white;
    alternate-background-color: #F8FAFC;
    border: 1px solid #D8DEE8;
    border-radius: 8px;
    gridline-color: #EEF2F7;
    selection-background-color: #DBEAFE;
    selection-color: #172033;
}
QHeaderView::section {
    background: #EEF2F7;
    color: #475569;
    border: none;
    border-bottom: 1px solid #D8DEE8;
    padding: 9px;
    font-weight: 600;
}
QStatusBar {
    background: white;
    color: #657084;
    border-top: 1px solid #E2E8F0;
}
"""
