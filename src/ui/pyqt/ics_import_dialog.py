"""Preview and confirm dialog for iCalendar imports."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from logic.ical_import import ICSImportPlan


class IcsImportDialog(QDialog):
    """Show a preview of the planned import and confirm what to commit."""

    def __init__(self, plan: ICSImportPlan, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import calendar events")
        self.resize(760, 460)
        self._plan = plan
        self._checks: list[QCheckBox] = []

        layout = QVBoxLayout(self)

        summary = (
            f"{plan.event_count} events found · {plan.ready} ready to import · "
            f"{plan.duplicates} already exist · "
            f"{len(plan.skipped)} unsupported"
        )
        heading = QLabel(summary)
        heading.setObjectName("SectionHeading")
        layout.addWidget(heading)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Import", "Date / time", "Details"])
        vertical_header = self.table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, header.ResizeMode.Stretch)
        layout.addWidget(self.table, 1)

        note = QLabel(
            "Unsupported and duplicate events are shown for review and will be "
            "skipped. Cancel to avoid any change to your tasks."
        )
        note.setObjectName("MutedLabel")
        layout.addWidget(note)

        buttons = QDialogButtonBox()
        cancel = buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        self.import_button = buttons.addButton(
            "Import", QDialogButtonBox.ButtonRole.AcceptRole
        )
        assert cancel is not None
        assert self.import_button is not None
        cancel.clicked.connect(self.reject)
        self.import_button.clicked.connect(self.accept)
        layout.addWidget(buttons)

        self._populate()
        self._update_state()

    def confirmed_tasks(self):
        """Return the checked Task objects the caller should commit."""
        selected = [
            index for index, check in enumerate(self._checks) if check.isChecked()
        ]
        return [self._plan.tasks[index] for index in selected]

    def _populate(self):
        for task in self._plan.tasks:
            check = QCheckBox()
            check.setChecked(True)
            check.toggled.connect(self._update_state)
            self._checks.append(check)
            row = self.table.rowCount()
            self.table.insertRow(row)
            cell = QTableWidgetItem()
            cell.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, cell)
            self.table.setCellWidget(row, 0, check)
            self.table.setItem(row, 1, QTableWidgetItem(f"{task.date} {task.time}"))
            self.table.setItem(row, 2, QTableWidgetItem(task.text))
        for _index in range(self._plan.duplicates):
            self._append_status_row("", "Already exists — will be skipped")
        for skipped in self._plan.skipped:
            self._append_status_row("", f"{skipped.text} — {skipped.reason}")

    def _append_status_row(self, date_text, detail):
        row = self.table.rowCount()
        self.table.insertRow(row)
        cell = QTableWidgetItem()
        cell.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 0, cell)
        date_item = QTableWidgetItem(date_text)
        date_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 1, date_item)
        detail_item = QTableWidgetItem(detail)
        detail_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        detail_item.setToolTip(detail)
        self.table.setItem(row, 2, detail_item)

    def _update_state(self):
        self.import_button.setEnabled(any(check.isChecked() for check in self._checks))
