"""
add_task_dialog.py
------------------
Improved modal dialog for adding a task.

- Pre-fills date/time with current values
- Adds keyboard shortcuts (Enter/Esc)
- Adds simple validation
- Cleaner layout and spacing
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class AddTaskDialog(tk.Toplevel):
    """Modal dialog for entering task details."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Task")
        self.resizable(False, False)

        self.result = None

        # ---------------------------------------------------------
        # Frame
        # ---------------------------------------------------------
        frame = ttk.Frame(self, padding=15)
        frame.grid(row=0, column=0)

        # ---------------------------------------------------------
        # Default values
        # ---------------------------------------------------------
        now = datetime.now()
        default_date = now.strftime("%Y-%m-%d")
        default_time = now.strftime("%H:%M")

        # ---------------------------------------------------------
        # Date
        # ---------------------------------------------------------
        ttk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", pady=4)
        self.date_entry = ttk.Entry(frame, width=25)
        self.date_entry.insert(0, default_date)
        self.date_entry.grid(row=0, column=1, pady=4)

        # ---------------------------------------------------------
        # Time
        # ---------------------------------------------------------
        ttk.Label(frame, text="Time (HH:MM):").grid(row=1, column=0, sticky="w", pady=4)
        self.time_entry = ttk.Entry(frame, width=25)
        self.time_entry.insert(0, default_time)
        self.time_entry.grid(row=1, column=1, pady=4)

        # ---------------------------------------------------------
        # Task title
        # ---------------------------------------------------------
        ttk.Label(frame, text="Task:").grid(row=2, column=0, sticky="w", pady=4)
        self.text_entry = ttk.Entry(frame, width=25)
        self.text_entry.grid(row=2, column=1, pady=4)

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(12, 0))

        ttk.Button(btn_frame, text="Cancel", command=self._cancel).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Add", command=self._on_add).grid(row=0, column=1, padx=6)

        # ---------------------------------------------------------
        # Keyboard shortcuts
        # ---------------------------------------------------------
        self.bind("<Return>", lambda e: self._on_add())
        self.bind("<Escape>", lambda e: self._cancel())

        # ---------------------------------------------------------
        # Focus
        # ---------------------------------------------------------
        self.text_entry.focus()

        # Modal behavior
        self.grab_set()
        self.wait_window()

    # -------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------
    def _cancel(self):
        self.result = None
        self.destroy()

    def _on_add(self):
        """Validate, collect values, and close dialog."""
        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        text = self.text_entry.get().strip()

        # Simple validation
        if not (date and time and text):
            self._flash_error()
            return

        self.result = (date, time, text)
        self.destroy()

    # -------------------------------------------------------------
    # UX: Flash red border on invalid input
    # -------------------------------------------------------------
    def _flash_error(self):
        for widget in (self.date_entry, self.time_entry, self.text_entry):
            widget.configure(style="Error.TEntry")

        self.after(150, self._clear_error)

    def _clear_error(self):
        for widget in (self.date_entry, self.time_entry, self.text_entry):
            widget.configure(style="TEntry")
