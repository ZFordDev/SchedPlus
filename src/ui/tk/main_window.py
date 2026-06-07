"""
main_window.py
--------------
Primary Tkinter window for SchedPlus (Basic Mode).

A modernized task manager UI with modal task entry, a refreshed task table,
and improved keyboard shortcuts for faster task handling.
"""

import tkinter as tk
from tkinter import ttk

from .add_task_dialog import AddTaskDialog
from .connector import TkConnector
from .utils import split_due_date


def run_ui(scheduler):
    """Entry point called by startup controller."""
    connector = TkConnector(scheduler)

    root = tk.Tk()
    root.title("SchedPlus")
    root.geometry("560x560")
    root.minsize(520, 520)
    root.configure(bg="#edf2fb")

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Root.TFrame", background="#edf2fb")
    style.configure("Card.TFrame", background="#ffffff", relief="flat")
    style.configure("Header.TLabel", background="#edf2fb", font=("Segoe UI", 16, "bold"), foreground="#1f2937")
    style.configure("SubHeader.TLabel", background="#edf2fb", font=("Segoe UI", 10), foreground="#4b5563")
    style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#4f46e5", padding=10)
    style.map("Accent.TButton", background=[("active", "#4338ca"), ("pressed", "#3730a3")])
    style.configure("Secondary.TButton", font=("Segoe UI", 10), foreground="#111827", background="#f3f4f6", padding=8)
    style.configure("Task.Treeview", background="#ffffff", fieldbackground="#ffffff", highlightthickness=0, bordercolor="#d1d5db", borderwidth=1)
    style.configure("Task.Treeview.Heading", font=("Segoe UI", 10, "bold"), foreground="#111827")
    style.map("Task.Treeview", background=[("selected", "#e0e7ff")])

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    container = ttk.Frame(root, style="Root.TFrame", padding=(18, 18, 18, 12))
    container.grid(row=0, column=0, sticky="nsew")
    container.columnconfigure(0, weight=1)
    container.rowconfigure(3, weight=1)

    header_frame = ttk.Frame(container, style="Root.TFrame")
    header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 14))
    header_frame.columnconfigure(0, weight=1)

    heading = ttk.Label(header_frame, text="SchedPlus", style="Header.TLabel")
    heading.grid(row=0, column=0, sticky="w")

    subtitle = ttk.Label(
        header_frame,
        text="A clean way to add tasks, track due times, and stay organized.",
        style="SubHeader.TLabel"
    )
    subtitle.grid(row=1, column=0, sticky="w", pady=(6, 0))

    # Quick action row.
    action_frame = ttk.Frame(container, style="Card.TFrame", padding=14)
    action_frame.grid(row=1, column=0, sticky="ew", pady=(0, 14))
    action_frame.columnconfigure(0, weight=1)
    action_frame.columnconfigure(1, weight=0)

    info_text = ttk.Label(
        action_frame,
        text="Use the button below to add a task with full date, time, and title.",
        style="SubHeader.TLabel",
        wraplength=360,
        justify="left"
    )
    info_text.grid(row=0, column=0, sticky="w")

    add_button = ttk.Button(action_frame, text="Add Task", style="Accent.TButton")
    add_button.grid(row=0, column=1, sticky="e")

    control_frame = ttk.Frame(container, style="Root.TFrame")
    control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
    control_frame.columnconfigure(0, weight=1)
    control_frame.columnconfigure(1, weight=0)
    control_frame.columnconfigure(2, weight=0)

    task_count_label = ttk.Label(control_frame, text="0 tasks", style="SubHeader.TLabel")
    task_count_label.grid(row=0, column=0, sticky="w")

    refresh_button = ttk.Button(control_frame, text="Refresh", style="Secondary.TButton")
    refresh_button.grid(row=0, column=1, sticky="e", padx=(0, 8))

    help_button = ttk.Button(control_frame, text="Help", style="Secondary.TButton")
    help_button.grid(row=0, column=2, sticky="e")

    list_frame = ttk.Frame(container, style="Card.TFrame", padding=12)
    list_frame.grid(row=3, column=0, sticky="nsew")
    list_frame.columnconfigure(0, weight=1)
    list_frame.rowconfigure(0, weight=1)

    task_table = ttk.Treeview(
        list_frame,
        columns=("date", "time", "task"),
        show="headings",
        style="Task.Treeview",
        selectmode="browse",
        height=14,
    )
    task_table.heading("date", text="Date")
    task_table.heading("time", text="Time")
    task_table.heading("task", text="Task")
    task_table.column("date", width=100, anchor="center")
    task_table.column("time", width=80, anchor="center")
    task_table.column("task", anchor="w")
    task_table.grid(row=0, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=task_table.yview)
    scrollbar.grid(row=0, column=1, sticky="ns", padx=(8, 0))
    task_table.configure(yscrollcommand=scrollbar.set)

    empty_state = ttk.Label(
        list_frame,
        text="No tasks yet. Click Add Task to create your first item.",
        style="SubHeader.TLabel",
        anchor="center"
    )
    empty_state.grid(row=0, column=0, sticky="nsew")

    def _update_empty_state():
        has_tasks = len(task_table.get_children()) > 0
        empty_state.lift() if not has_tasks else empty_state.lower()

    def refresh_task_list():
        task_table.delete(*task_table.get_children())
        for index, entry in enumerate(connector.list_tasks()):
            date, time = split_due_date(entry.due_date)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            task_table.insert("", tk.END, values=(date, time, entry.title), tags=(tag,))

        task_table.tag_configure("evenrow", background="#ffffff")
        task_table.tag_configure("oddrow", background="#f8fafc")
        task_count_label.configure(text=f"{len(task_table.get_children())} tasks")
        _update_empty_state()

    def open_add_task_dialog(event=None):
        dialog = AddTaskDialog(root)
        if not dialog.result:
            return

        date, time, title = dialog.result
        if connector.add_task(date, time, title):
            refresh_task_list()

    def show_help():
        help_text = (
            "Enter a date in YYYY-MM-DD format, a time in HH:MM format,\n"
            "and a short task title. Use Add Task to save it. \n"
            "Refresh updates the task list when changes occur."
        )
        help_dialog = tk.Toplevel(root)
        help_dialog.title("Help")
        help_dialog.resizable(False, False)
        help_frame = ttk.Frame(help_dialog, padding=16)
        help_frame.grid(row=0, column=0)
        ttk.Label(help_frame, text="How to use SchedPlus", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        ttk.Label(help_frame, text=help_text, font=("Segoe UI", 10), foreground="#374151", justify="left").grid(row=1, column=0, sticky="w")
        ttk.Button(help_frame, text="Close", command=help_dialog.destroy, style="Accent.TButton").grid(row=2, column=0, pady=(14, 0), sticky="e")
        help_dialog.grab_set()
        help_dialog.transient(root)
        help_dialog.wait_window()

    add_button.configure(command=open_add_task_dialog)
    refresh_button.configure(command=refresh_task_list)
    help_button.configure(command=show_help)

    root.bind("<Control-n>", open_add_task_dialog)
    root.bind("<Control-r>", lambda event: refresh_task_list())

    refresh_task_list()
    root.mainloop()
