"""Lightweight, user-friendly Tkinter interface for SchedPlus."""

import logging
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from logic.scheduler import Scheduler
from tkcalendar import Calendar
from ui.shortcuts import bind_enter_key
from ui.validation import add_validated_task


LOGGER = logging.getLogger(__name__)

BACKGROUND = "#F4F6F8"
SURFACE = "#FFFFFF"
TEXT = "#172033"
MUTED = "#657084"
ACCENT = "#2563EB"
ACCENT_ACTIVE = "#1D4ED8"
BORDER = "#DCE1E8"
SUCCESS = "#16794A"


def _configure_styles(root: tk.Tk) -> None:
    """Apply a small, consistent visual system to the fallback interface."""
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    root.configure(background=BACKGROUND)
    style.configure("App.TFrame", background=BACKGROUND)
    style.configure("Surface.TFrame", background=SURFACE)
    style.configure(
        "Title.TLabel",
        background=BACKGROUND,
        foreground=TEXT,
        font=("Segoe UI", 20, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=BACKGROUND,
        foreground=MUTED,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Section.TLabel",
        background=SURFACE,
        foreground=TEXT,
        font=("Segoe UI", 11, "bold"),
    )
    style.configure(
        "Field.TLabel",
        background=SURFACE,
        foreground=TEXT,
        font=("Segoe UI", 9),
    )
    style.configure(
        "Hint.TLabel",
        background=SURFACE,
        foreground=MUTED,
        font=("Segoe UI", 9),
    )
    style.configure(
        "Status.TLabel",
        background=BACKGROUND,
        foreground=MUTED,
        font=("Segoe UI", 9),
    )
    style.configure(
        "Success.Status.TLabel",
        background=BACKGROUND,
        foreground=SUCCESS,
        font=("Segoe UI", 9),
    )
    style.configure(
        "TEntry",
        fieldbackground=SURFACE,
        foreground=TEXT,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=(9, 7),
    )
    style.map("TEntry", bordercolor=[("focus", ACCENT)])
    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="#FFFFFF",
        borderwidth=0,
        padding=(16, 9),
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Accent.TButton",
        background=[("active", ACCENT_ACTIVE), ("pressed", ACCENT_ACTIVE)],
    )
    style.configure(
        "Picker.TButton",
        background="#EEF2F7",
        foreground=TEXT,
        borderwidth=0,
        padding=(8, 7),
    )
    style.map("Picker.TButton", background=[("active", "#E2E8F0")])
    style.configure(
        "Treeview",
        background=SURFACE,
        fieldbackground=SURFACE,
        foreground=TEXT,
        bordercolor=BORDER,
        rowheight=30,
        font=("Segoe UI", 9),
    )
    style.configure(
        "Treeview.Heading",
        background="#EEF2F7",
        foreground=TEXT,
        relief="flat",
        padding=(8, 7),
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Treeview",
        background=[("selected", "#DBEAFE")],
        foreground=[("selected", TEXT)],
    )


def _center_window(window: tk.Toplevel | tk.Tk) -> None:
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = max(0, (window.winfo_screenwidth() - width) // 2)
    y = max(0, (window.winfo_screenheight() - height) // 2)
    window.geometry(f"+{x}+{y}")


def run_ui(scheduler: Scheduler) -> None:
    root = tk.Tk()
    root.title("SchedPlus")
    root.geometry("680x600")
    root.minsize(560, 500)
    root.option_add("*tearOff", False)
    _configure_styles(root)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    container = ttk.Frame(root, style="App.TFrame", padding=(24, 20, 24, 16))
    container.grid(row=0, column=0, sticky="nsew")
    container.columnconfigure(0, weight=1)
    container.rowconfigure(2, weight=1)

    # Header
    header = ttk.Frame(container, style="App.TFrame")
    header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
    header.columnconfigure(0, weight=1)
    ttk.Label(header, text="SchedPlus", style="Title.TLabel").grid(
        row=0, column=0, sticky="w"
    )
    ttk.Label(
        header,
        text="Plan your day without the clutter.",
        style="Subtitle.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(2, 0))

    # Add-task card
    form = ttk.Frame(container, style="Surface.TFrame", padding=16)
    form.grid(row=1, column=0, sticky="ew", pady=(0, 16))
    form.columnconfigure(0, weight=1)
    form.columnconfigure(1, weight=1)

    ttk.Label(form, text="Add a task", style="Section.TLabel").grid(
        row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
    )

    ttk.Label(form, text="Date", style="Field.TLabel").grid(
        row=1, column=0, sticky="w", padx=(0, 8)
    )
    ttk.Label(form, text="Time", style="Field.TLabel").grid(
        row=1, column=1, sticky="w", padx=(8, 0)
    )

    date_row = ttk.Frame(form, style="Surface.TFrame")
    date_row.grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
    date_row.columnconfigure(0, weight=1)
    date_entry = ttk.Entry(date_row)
    date_entry.grid(row=0, column=0, sticky="ew")
    date_entry.insert(0, date.today().isoformat())

    time_row = ttk.Frame(form, style="Surface.TFrame")
    time_row.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(4, 10))
    time_row.columnconfigure(0, weight=1)
    time_entry = ttk.Entry(time_row)
    time_entry.grid(row=0, column=0, sticky="ew")
    time_entry.insert(0, datetime.now().strftime("%H:%M"))

    ttk.Label(form, text="What needs to be done?", style="Field.TLabel").grid(
        row=3, column=0, columnspan=2, sticky="w"
    )
    task_entry = ttk.Entry(form)
    task_entry.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 12))

    actions = ttk.Frame(form, style="Surface.TFrame")
    actions.grid(row=5, column=0, columnspan=2, sticky="ew")
    actions.columnconfigure(0, weight=1)
    ttk.Label(actions, text="Press Enter to add", style="Hint.TLabel").grid(
        row=0, column=0, sticky="w"
    )
    add_button = ttk.Button(actions, text="Add task", style="Accent.TButton")
    add_button.grid(row=0, column=1, sticky="e")

    def open_calendar() -> None:
        picker = tk.Toplevel(root)
        picker.title("Choose a date")
        picker.resizable(False, False)
        picker.transient(root)
        picker.grab_set()

        calendar = Calendar(picker, selectmode="day", date_pattern="yyyy-mm-dd")
        calendar.pack(padx=16, pady=(16, 10))

        def choose_date() -> None:
            date_entry.delete(0, tk.END)
            date_entry.insert(0, calendar.get_date())
            picker.destroy()

        ttk.Button(
            picker, text="Use this date", style="Accent.TButton", command=choose_date
        ).pack(pady=(0, 16))
        picker.bind("<Escape>", lambda _event: picker.destroy())
        _center_window(picker)

    def open_time_picker() -> None:
        picker = tk.Toplevel(root)
        picker.title("Choose a time")
        picker.resizable(False, False)
        picker.transient(root)
        picker.grab_set()

        content = ttk.Frame(picker, padding=16)
        content.grid(row=0, column=0)
        now = datetime.now()
        hour = tk.StringVar(value=now.strftime("%H"))
        minute = tk.StringVar(value=now.strftime("%M"))

        ttk.Label(content, text="Hour").grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        ttk.Label(content, text="Minute").grid(
            row=0, column=1, sticky="w", padx=(8, 0)
        )
        ttk.Spinbox(
            content,
            from_=0,
            to=23,
            width=5,
            format="%02.0f",
            textvariable=hour,
            wrap=True,
        ).grid(row=1, column=0, padx=(0, 8), pady=(4, 14))
        ttk.Spinbox(
            content,
            from_=0,
            to=59,
            width=5,
            format="%02.0f",
            textvariable=minute,
            wrap=True,
        ).grid(row=1, column=1, padx=(8, 0), pady=(4, 14))

        def choose_time() -> None:
            try:
                selected = f"{int(hour.get()):02d}:{int(minute.get()):02d}"
                datetime.strptime(selected, "%H:%M")
            except ValueError:
                messagebox.showerror(
                    "Invalid time",
                    "Choose an hour from 00–23 and minute from 00–59.",
                    parent=picker,
                )
                return
            time_entry.delete(0, tk.END)
            time_entry.insert(0, selected)
            picker.destroy()

        ttk.Button(
            content, text="Use this time", style="Accent.TButton", command=choose_time
        ).grid(row=2, column=0, columnspan=2, sticky="ew")
        picker.bind("<Escape>", lambda _event: picker.destroy())
        _center_window(picker)

    ttk.Button(
        date_row,
        text="Calendar",
        style="Picker.TButton",
        command=open_calendar,
    ).grid(row=0, column=1, padx=(6, 0))
    ttk.Button(
        time_row,
        text="Time",
        style="Picker.TButton",
        command=open_time_picker,
    ).grid(row=0, column=1, padx=(6, 0))

    # Task list
    tasks_panel = ttk.Frame(container, style="Surface.TFrame", padding=16)
    tasks_panel.grid(row=2, column=0, sticky="nsew")
    tasks_panel.columnconfigure(0, weight=1)
    tasks_panel.rowconfigure(1, weight=1)

    list_header = ttk.Frame(tasks_panel, style="Surface.TFrame")
    list_header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
    list_header.columnconfigure(0, weight=1)
    ttk.Label(list_header, text="Your tasks", style="Section.TLabel").grid(
        row=0, column=0, sticky="w"
    )
    task_count = ttk.Label(list_header, style="Hint.TLabel")
    task_count.grid(row=0, column=1, sticky="e")

    task_list = ttk.Treeview(
        tasks_panel,
        columns=("date", "time", "text"),
        show="headings",
        selectmode="browse",
    )
    task_list.heading("date", text="Date")
    task_list.heading("time", text="Time")
    task_list.heading("text", text="Task")
    task_list.column("date", width=110, minwidth=100, anchor="center", stretch=False)
    task_list.column("time", width=75, minwidth=65, anchor="center", stretch=False)
    task_list.column("text", width=360, minwidth=180, anchor="w")
    task_list.grid(row=1, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(tasks_panel, orient="vertical", command=task_list.yview)
    scrollbar.grid(row=1, column=1, sticky="ns")
    task_list.configure(yscrollcommand=scrollbar.set)

    status = ttk.Label(container, text="Ready", style="Status.TLabel")
    status.grid(row=3, column=0, sticky="w", pady=(10, 0))

    def update_task_count() -> None:
        count = len(task_list.get_children())
        task_count.configure(text=f"{count} task" if count == 1 else f"{count} tasks")

    for task in scheduler.get_tasks():
        task_list.insert("", "end", values=(task.date, task.time, task.text))
    update_task_count()

    def set_status(message: str, *, success: bool = False) -> None:
        status.configure(
            text=message,
            style="Success.Status.TLabel" if success else "Status.TLabel",
        )

    def add_task() -> bool:
        try:
            new_task = add_validated_task(
                scheduler,
                date_entry.get(),
                time_entry.get(),
                task_entry.get(),
            )
            task_list.insert(
                "", "end", values=(new_task.date, new_task.time, new_task.text)
            )
            task_entry.delete(0, tk.END)
            task_entry.focus_set()
            update_task_count()
            set_status("Task added successfully", success=True)
            return True
        except ValueError as exc:
            LOGGER.warning("Task validation failed: %s", exc)
            set_status(str(exc))
            messagebox.showerror("Check task details", str(exc), parent=root)
        except Exception as exc:
            LOGGER.exception("Unable to add task from the Tkinter interface")
            set_status("Task could not be saved")
            messagebox.showerror(
                "Unable to add task",
                "SchedPlus could not save this task. Please try again.\n\n"
                f"Details: {exc}",
                parent=root,
            )
        return False

    add_button.configure(command=add_task)
    bind_enter_key([date_entry, time_entry, task_entry], add_task)
    root.bind("<Escape>", lambda _event: root.focus_set())
    task_entry.focus_set()
    _center_window(root)
    root.mainloop()
