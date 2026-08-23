"""Application-wide styling for the advanced native interface."""

from __future__ import annotations

from PyQt6.QtGui import QColor, QPalette

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
QLabel#SidebarVersion {
    color: #94A3B8;
    font-size: 9pt;
    padding: 10px 12px 0 12px;
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
QLabel#SectionHeading {
    color: #172033;
    font-size: 11pt;
    font-weight: 600;
    padding: 2px 0;
}
QLabel#EmptyState {
    color: #657084;
    background: #FFFFFF;
    border: 1px dashed #CBD5E1;
    border-radius: 8px;
    padding: 20px;
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
QComboBox {
    min-width: 120px;
    padding-right: 28px;
}
QComboBox::drop-down {
    width: 26px;
    border: none;
    border-left: 1px solid #E2E8F0;
}
QComboBox QAbstractItemView {
    background: #FFFFFF;
    color: #172033;
    border: 1px solid #CBD5E1;
    outline: 0;
    selection-background-color: #DBEAFE;
    selection-color: #172033;
    padding: 4px;
}
QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 5px 8px;
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
QListWidget {
    background: #FFFFFF;
    color: #172033;
    alternate-background-color: #F8FAFC;
    border: 1px solid #D8DEE8;
    border-radius: 8px;
    padding: 4px;
    outline: 0;
}
QListWidget::item {
    min-height: 30px;
    padding: 6px 8px;
    border-radius: 5px;
}
QListWidget::item:selected {
    background: #DBEAFE;
    color: #172033;
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
QScrollBar:vertical {
    background: #EEF2F7;
    width: 12px;
    margin: 0;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #C4CEDA;
    border-radius: 5px;
    min-height: 30px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}
QScrollBar:horizontal {
    background: #EEF2F7;
    height: 12px;
    margin: 0;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background: #C4CEDA;
    border-radius: 5px;
    min-width: 30px;
    margin: 2px;
}
QScrollBar::handle:horizontal:hover {
    background: #94A3B8;
}
QScrollBar::add-line, QScrollBar::sub-line {
    height: 0;
    width: 0;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
}
QMenuBar {
    background: #FFFFFF;
    color: #172033;
    border-bottom: 1px solid #E2E8F0;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
}
QMenuBar::item:selected {
    background: #DBEAFE;
}
QMenuBar::item:pressed {
    background: #DBEAFE;
}
QMenu {
    background: #FFFFFF;
    color: #172033;
    border: 1px solid #CBD5E1;
    padding: 4px;
    outline: 0;
}
QMenu::item {
    padding: 7px 22px 7px 12px;
    border-radius: 5px;
}
QMenu::item:selected {
    background: #DBEAFE;
    color: #172033;
}
QMenu::item:disabled {
    color: #94A3B8;
}
QMenu::separator {
    height: 1px;
    background: #E2E8F0;
    margin: 4px 8px;
}
QSpinBox {
    background: white;
    border: 1px solid #D8DEE8;
    border-radius: 6px;
    padding: 8px 10px;
    min-height: 18px;
    selection-background-color: #DBEAFE;
    selection-color: #172033;
}
QSpinBox:focus {
    border-color: #2563EB;
}
QSpinBox::up-button, QSpinBox::down-button {
    background: transparent;
    border: none;
    width: 18px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: #EEF2F7;
    border-radius: 4px;
}
QSpinBox::up-arrow {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #657084;
}
QSpinBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #657084;
}
QSpinBox::up-arrow:hover, QSpinBox::down-arrow:hover {
    border-top-color: #2563EB;
    border-bottom-color: #2563EB;
}
QTabWidget::pane {
    background: #FFFFFF;
    border: 1px solid #D8DEE8;
    border-radius: 8px;
}
QTabBar::tab {
    background: #EEF2F7;
    color: #475569;
    padding: 8px 16px;
    border: 1px solid #D8DEE8;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #FFFFFF;
    color: #172033;
    font-weight: 600;
}
QTabBar::tab:hover:!selected {
    background: #E2E8F0;
}
QGroupBox {
    background: #FFFFFF;
    border: 1px solid #D8DEE8;
    border-radius: 8px;
    margin-top: 12px;
    padding: 8px 4px 4px 4px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #475569;
    font-weight: 600;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #D8DEE8;
    border-radius: 4px;
    background: white;
}
QCheckBox::indicator:hover {
    border-color: #CBD5E1;
}
QCheckBox::indicator:checked {
    background: #2563EB;
    border-color: #2563EB;
}
QCheckBox::indicator:disabled {
    background: #E8ECF1;
    border-color: #E8ECF1;
}
QToolTip {
    background: #172033;
    color: #FFFFFF;
    border: none;
    padding: 6px 8px;
    border-radius: 4px;
}
QSplitter::handle {
    background: #E2E8F0;
}
QSplitter::handle:hover {
    background: #CBD5E1;
}
QDialogButtonBox QPushButton {
    min-width: 80px;
    background: white;
    color: #172033;
    border: 1px solid #D8DEE8;
}
QDialogButtonBox QPushButton:hover {
    background: #EEF2F7;
}
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
}
QCalendarWidget QToolButton {
    background: transparent;
    color: #172033;
    border-radius: 6px;
    padding: 4px 8px;
    font-weight: 600;
}
QCalendarWidget QToolButton:hover {
    background: #EEF2F7;
}
QCalendarWidget QToolButton::menu-indicator {
    image: none;
}
QCalendarWidget QAbstractItemView {
    background: #FFFFFF;
    color: #172033;
    outline: 0;
    selection-background-color: #DBEAFE;
    selection-color: #172033;
}
"""

# Palette mirrors the QSS tokens above so any widget class without explicit
# rules still renders on-brand instead of inheriting a dark system palette.
_PALETTE_TOKENS = {
    QPalette.ColorRole.Window: "#F4F6F8",
    QPalette.ColorRole.WindowText: "#172033",
    QPalette.ColorRole.Base: "#FFFFFF",
    QPalette.ColorRole.AlternateBase: "#F8FAFC",
    QPalette.ColorRole.Text: "#172033",
    QPalette.ColorRole.Button: "#FFFFFF",
    QPalette.ColorRole.ButtonText: "#172033",
    QPalette.ColorRole.PlaceholderText: "#94A3B8",
    QPalette.ColorRole.Highlight: "#DBEAFE",
    QPalette.ColorRole.HighlightedText: "#172033",
    QPalette.ColorRole.Link: "#2563EB",
    QPalette.ColorRole.ToolTipBase: "#172033",
    QPalette.ColorRole.ToolTipText: "#FFFFFF",
    QPalette.ColorRole.BrightText: "#FFFFFF",
}

_DISABLED_TOKENS = {
    QPalette.ColorRole.WindowText: "#94A3B8",
    QPalette.ColorRole.Text: "#94A3B8",
    QPalette.ColorRole.ButtonText: "#94A3B8",
    QPalette.ColorRole.Base: "#E8ECF1",
}


def application_palette() -> QPalette:
    """Return a QPalette built from the same tokens as ``BASE_QSS``."""
    palette = QPalette()
    for role, color in _PALETTE_TOKENS.items():
        palette.setColor(role, QColor(color))
    for role, color in _DISABLED_TOKENS.items():
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(color))
    return palette


def install_theme(app) -> None:
    """Apply the fallback palette so uncovered widgets stay on-brand."""
    app.setPalette(application_palette())
