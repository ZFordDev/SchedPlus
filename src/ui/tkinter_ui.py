"""Lightweight, user-friendly Tkinter interface for SchedPlus."""

import logging
import queue
import tkinter as tk
from datetime import date, datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from dataclasses import replace

from tkcalendar import Calendar

from logic.data_transfer import (
    DataTransferError,
    create_backup,
    export_tasks,
    import_tasks,
    restore_backup,
)
from logic.scheduler import Scheduler
from logic.storage.sqlite_storage import StorageError
from logic.validation import ValidationError
from schedplus.identity import get_application_identity
from ui.shortcuts import bind_enter_key
from updater.background import start_automatic_update, start_update_check
from updater.config import load_build_info
from updater.errors import UpdateError
from updater.preferences import (
    UpdatePreferences,
    load_update_preferences,
    save_update_preferences,
)
from updater.service import launch_prepared_update
from updater.state import read_state

LOGGER = logging.getLogger(__name__)

BACKGROUND = "#F4F6F8"
SURFACE = "#FFFFFF"
TEXT = "#172033"
MUTED = "#657084"
ACCENT = "#2563EB"
ACCENT_ACTIVE = "#1D4ED8"
BORDER = "#DCE1E8"
SUCCESS = "#16794A"


def _tk_data_action(root, operation, success_message: str) -> None:
    try:
        operation()
        messagebox.showinfo("SchedPlus", success_message, parent=root)
    except (DataTransferError, StorageError) as exc:
        messagebox.showerror("Data operation failed", str(exc), parent=root)


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


def _update_status_text() -> str:
    try:
        state = read_state()
    except UpdateError as exc:
        return str(exc)
    lines = [f"Status: {state.status}"]
    if state.target_version:
        lines.append(f"Target version: {state.target_version}")
    if state.message:
        lines.append(state.message)
    return "\n".join(lines)


def run_ui(scheduler: Scheduler, startup_notice: str | None = None) -> None:
    identity = get_application_identity()
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

        ttk.Label(content, text="Hour").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Label(content, text="Minute").grid(row=0, column=1, sticky="w", padx=(8, 0))
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

    search_frame = ttk.Frame(tasks_panel, style="Surface.TFrame")
    search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
    search_frame.columnconfigure(0, weight=1)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
    search_entry.insert(0, "")
    filter_var = tk.StringVar(value="all")
    filter_combo = ttk.Combobox(
        search_frame,
        textvariable=filter_var,
        values=["all", "active", "completed"],
        state="readonly",
        width=12,
    )
    filter_combo.grid(row=0, column=1, sticky="e")

    task_list = ttk.Treeview(
        tasks_panel,
        columns=("date", "time", "text", "status"),
        show="headings",
        selectmode="browse",
    )
    task_list.heading("date", text="Date")
    task_list.heading("time", text="Time")
    task_list.heading("text", text="Task")
    task_list.heading("status", text="Status")
    task_list.column("date", width=110, minwidth=100, anchor="center", stretch=False)
    task_list.column("time", width=75, minwidth=65, anchor="center", stretch=False)
    task_list.column("text", width=300, minwidth=180, anchor="w")
    task_list.column("status", width=80, minwidth=70, anchor="center", stretch=False)
    task_list.grid(row=2, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(tasks_panel, orient="vertical", command=task_list.yview)
    scrollbar.grid(row=2, column=1, sticky="ns")
    task_list.configure(yscrollcommand=scrollbar.set)

    footer = ttk.Frame(container, style="App.TFrame")
    footer.grid(row=3, column=0, sticky="ew", pady=(10, 0))
    footer.columnconfigure(0, weight=1)
    status = ttk.Label(footer, text="Ready", style="Status.TLabel")
    status.grid(row=0, column=0, sticky="w")
    ttk.Label(footer, text=identity.version_label, style="Status.TLabel").grid(
        row=0, column=1, sticky="e"
    )

    show_completed = tk.BooleanVar(value=False)

    def update_task_count() -> None:
        count = len(task_list.get_children())
        task_count.configure(text=f"{count} task" if count == 1 else f"{count} tasks")

    def refresh_task_list() -> None:
        task_list.delete(*task_list.get_children())
        search = search_var.get().strip().casefold()
        filt = filter_var.get()
        for task in scheduler.get_tasks():
            is_completed = task.completed == "true"
            if is_completed and not show_completed.get():
                continue
            if filt == "active" and is_completed:
                continue
            if filt == "completed" and not is_completed:
                continue
            if search and search not in task.text.casefold():
                continue
            status = "Done" if is_completed else ""
            task_list.insert("", "end", values=(task.date, task.time, task.text, status))
        update_task_count()

    refresh_task_list()

    task_actions = ttk.Frame(tasks_panel, style="Surface.TFrame")
    task_actions.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    task_actions.columnconfigure(0, weight=1)
    ttk.Checkbutton(
        task_actions,
        text="Show completed",
        variable=show_completed,
        command=refresh_task_list,
    ).grid(row=0, column=0, sticky="w")
    edit_button = ttk.Button(task_actions, text="Edit")
    edit_button.grid(row=0, column=1, sticky="e", padx=(0, 4))
    delete_button = ttk.Button(task_actions, text="Delete")
    delete_button.grid(row=0, column=2, sticky="e", padx=(0, 4))
    complete_button = ttk.Button(task_actions, text="Mark complete")
    complete_button.grid(row=0, column=3, sticky="e")

    def set_status(message: str, *, success: bool = False) -> None:
        status.configure(
            text=message,
            style="Success.Status.TLabel" if success else "Status.TLabel",
        )

    def complete_selected_task() -> None:
        selected = task_list.selection()
        if not selected:
            set_status("Select a task to mark complete")
            return
        item = selected[0]
        values = task_list.item(item, "values")
        task_text = values[2]
        task_to_complete = None
        for t in scheduler.get_tasks():
            if t.text == task_text and t.date == values[0] and t.time == values[1]:
                task_to_complete = t
                break
        if not task_to_complete:
            return
        try:
            if task_to_complete.completed == "true":
                scheduler.uncomplete_task(task_to_complete.id)
                set_status("Task marked as incomplete", success=True)
            else:
                scheduler.complete_task(task_to_complete.id)
                set_status("Task marked as complete", success=True)
            refresh_task_list()
        except StorageError as exc:
            set_status("Could not update task")
            messagebox.showerror("Unable to update task", str(exc), parent=root)

    def _selected_task():
        selected = task_list.selection()
        if not selected:
            return None
        item = selected[0]
        values = task_list.item(item, "values")
        for t in scheduler.get_tasks():
            if t.text == values[2] and t.date == values[0] and t.time == values[1]:
                return t
        return None

    def edit_selected_task() -> None:
        task = _selected_task()
        if not task:
            set_status("Select a task to edit")
            return
        dialog = tk.Toplevel(root)
        dialog.title("Edit task")
        dialog.resizable(False, False)
        dialog.transient(root)
        dialog.grab_set()
        content = ttk.Frame(dialog, padding=20)
        content.grid(row=0, column=0)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        ttk.Label(content, text="Edit task", style="Section.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )
        ttk.Label(content, text="Date", style="Field.TLabel").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Label(content, text="Time", style="Field.TLabel").grid(
            row=1, column=1, sticky="w"
        )
        edit_date = ttk.Entry(content)
        edit_date.grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
        edit_date.insert(0, task.date)
        edit_time = ttk.Entry(content)
        edit_time.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(4, 10))
        edit_time.insert(0, task.time)
        ttk.Label(content, text="Task", style="Field.TLabel").grid(
            row=3, column=0, columnspan=2, sticky="w"
        )
        edit_text = ttk.Entry(content)
        edit_text.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 10))
        edit_text.insert(0, task.text)
        ttk.Label(content, text="Notes", style="Field.TLabel").grid(
            row=5, column=0, columnspan=2, sticky="w"
        )
        edit_notes = ttk.Entry(content)
        edit_notes.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(4, 10))
        edit_notes.insert(0, getattr(task, "notes", "") or "")
        ttk.Label(content, text="Priority", style="Field.TLabel").grid(
            row=7, column=0, sticky="w"
        )
        ttk.Label(content, text="Duration (min)", style="Field.TLabel").grid(
            row=7, column=1, sticky="w"
        )
        priority_var = tk.StringVar(value=getattr(task, "priority", "") or "")
        priority_combo = ttk.Combobox(
            content,
            textvariable=priority_var,
            values=["", "low", "medium", "high"],
            state="readonly",
            width=12,
        )
        priority_combo.grid(row=8, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
        edit_duration = ttk.Entry(content)
        edit_duration.grid(row=8, column=1, sticky="ew", padx=(8, 0), pady=(4, 10))
        edit_duration.insert(0, getattr(task, "duration", "") or "")
        ttk.Label(content, text="Category", style="Field.TLabel").grid(
            row=9, column=0, columnspan=2, sticky="w"
        )
        edit_category = ttk.Entry(content)
        edit_category.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(4, 10))
        edit_category.insert(0, getattr(task, "category", "") or "")

        def save_edit() -> None:
            try:
                updated = replace(
                    task,
                    date=edit_date.get().strip(),
                    time=edit_time.get().strip(),
                    text=edit_text.get().strip(),
                    notes=edit_notes.get().strip(),
                    priority=priority_var.get(),
                    duration=edit_duration.get().strip(),
                    category=edit_category.get().strip(),
                )
                scheduler.update_task(updated)
                refresh_task_list()
                set_status("Task updated", success=True)
                dialog.destroy()
            except ValidationError as exc:
                messagebox.showerror("Invalid task", str(exc), parent=dialog)
            except StorageError as exc:
                messagebox.showerror("Unable to update task", str(exc), parent=dialog)

        buttons = ttk.Frame(content)
        buttons.grid(row=5, column=0, columnspan=2, sticky="ew")
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(
            buttons, text="Save", style="Accent.TButton", command=save_edit
        ).grid(row=0, column=1, sticky="e")
        dialog.bind("<Escape>", lambda _e: dialog.destroy())
        edit_text.focus_set()
        _center_window(dialog)

    def delete_selected_task() -> None:
        task = _selected_task()
        if not task:
            set_status("Select a task to delete")
            return
        if not messagebox.askyesno(
            "Delete task?",
            f'Delete "{task.text}"?\n\nThis cannot be undone.',
            parent=root,
        ):
            return
        try:
            scheduler.delete_task(task.id)
            refresh_task_list()
            set_status("Task deleted", success=True)
        except StorageError as exc:
            messagebox.showerror("Unable to delete task", str(exc), parent=root)

    update_events: queue.SimpleQueue = queue.SimpleQueue()

    def offer_prepared_update(build_info, prepared) -> None:
        action = (
            "Open the downloaded package folder?"
            if prepared.action == "download"
            else "Close SchedPlus and install it now?"
        )
        accepted = messagebox.askyesno(
            "SchedPlus update ready",
            f"SchedPlus {prepared.check.latest_version} is ready to install.\n\n{action}",
            parent=root,
        )
        if not accepted:
            set_status("Update postponed")
            return
        try:
            launch_prepared_update(build_info, prepared)
        except UpdateError as exc:
            messagebox.showerror("Unable to install update", str(exc), parent=root)
            return
        if prepared.action != "download":
            root.destroy()

    def poll_update_events() -> None:
        while not update_events.empty():
            kind, payload = update_events.get()
            if kind == "ready":
                offer_prepared_update(*payload)
            else:
                set_status(f"Update check failed: {payload}")
        root.after(250, poll_update_events)

    update_preferences = load_update_preferences()
    updates_managed_internally = load_build_info().internally_managed
    automatic_updates = tk.BooleanVar(
        root,
        value=(
            update_preferences.check_automatically if updates_managed_internally else False
        ),
    )

    def save_automatic_update_setting() -> None:
        if not updates_managed_internally:
            return
        try:
            save_update_preferences(UpdatePreferences(automatic_updates.get()))
            set_status("Update preference saved", success=True)
        except UpdateError as exc:
            messagebox.showerror(
                "Unable to save update settings", str(exc), parent=root
            )

    application_menu = tk.Menu(root)
    data_menu = tk.Menu(application_menu, tearoff=False)

    def choose_backup() -> None:
        path = filedialog.asksaveasfilename(
            parent=root,
            title="Create SchedPlus backup",
            defaultextension=".json",
            filetypes=(("JSON", "*.json"),),
        )
        if path:
            _tk_data_action(root, lambda: create_backup(Path(path)), "Backup created")

    def choose_restore() -> None:
        path = filedialog.askopenfilename(
            parent=root, title="Restore SchedPlus backup", filetypes=(("JSON", "*.json"),)
        )
        if not path or not messagebox.askyesno(
            "Replace current data?",
            "Restore will replace all current tasks and preferences. Continue?",
            parent=root,
        ):
            return
        try:
            result = restore_backup(Path(path))
            scheduler.load_tasks()
            refresh_task_list()
            messagebox.showinfo(
                "Backup restored",
                f"Restored {result.restored} task(s).\n\nPrevious data:\n{result.safety_backup}",
                parent=root,
            )
        except (DataTransferError, StorageError) as exc:
            messagebox.showerror("Unable to restore backup", str(exc), parent=root)

    def choose_export() -> None:
        path = filedialog.asksaveasfilename(
            parent=root,
            title="Export SchedPlus tasks",
            defaultextension=".json",
            filetypes=(("JSON", "*.json"),),
        )
        if path:
            _tk_data_action(root, lambda: export_tasks(Path(path)), "Tasks exported")

    def choose_import() -> None:
        path = filedialog.askopenfilename(
            parent=root, title="Import SchedPlus tasks", filetypes=(("JSON", "*.json"),)
        )
        if not path:
            return
        try:
            result = import_tasks(Path(path))
            scheduler.load_tasks()
            refresh_task_list()
            messagebox.showinfo(
                "Import complete",
                f"Imported {result.imported}; skipped {result.duplicates} duplicate(s) "
                f"and {result.conflicts} conflict(s).",
                parent=root,
            )
        except (DataTransferError, StorageError) as exc:
            messagebox.showerror("Unable to import tasks", str(exc), parent=root)

    data_menu.add_command(label="Create backup…", command=choose_backup)
    data_menu.add_command(label="Restore backup…", command=choose_restore)
    data_menu.add_separator()
    data_menu.add_command(label="Export tasks…", command=choose_export)
    data_menu.add_command(label="Import tasks…", command=choose_import)
    application_menu.add_cascade(label="Data", menu=data_menu)
    settings_menu = tk.Menu(application_menu, tearoff=False)
    settings_menu.add_checkbutton(
        label="Check for updates automatically",
        variable=automatic_updates,
        command=save_automatic_update_setting,
        state="normal" if updates_managed_internally else "disabled",
    )
    settings_menu.add_command(
        label="Check for updates now",
        command=lambda: start_update_check(
            lambda info, prepared: update_events.put(("ready", (info, prepared))),
            lambda message: update_events.put(("error", message)),
        ),
        state="normal" if updates_managed_internally else "disabled",
    )
    settings_menu.add_command(
        label="Last update result",
        command=lambda: messagebox.showinfo(
            "Last update result",
            _update_status_text(),
            parent=root,
        ),
    )
    application_menu.add_cascade(label="Settings", menu=settings_menu)
    help_menu = tk.Menu(application_menu, tearoff=False)
    help_menu.add_command(
        label="About SchedPlus",
        command=lambda: messagebox.showinfo(
            "About SchedPlus", identity.details, parent=root
        ),
    )
    application_menu.add_cascade(label="Help", menu=help_menu)
    root.configure(menu=application_menu)

    start_automatic_update(
        lambda info, prepared: update_events.put(("ready", (info, prepared))),
        lambda message: update_events.put(("error", message)),
    )
    root.after(250, poll_update_events)

    def add_task() -> bool:
        try:
            new_task = scheduler.add_task(
                date_entry.get(),
                time_entry.get(),
                task_entry.get(),
            )
            task_list.insert(
                "", "end", values=(new_task.date, new_task.time, new_task.text, "")
            )
            task_entry.delete(0, tk.END)
            task_entry.focus_set()
            update_task_count()
            set_status("Task added successfully", success=True)
            return True
        except ValidationError as exc:
            LOGGER.warning("Task validation failed: %s", exc)
            set_status(str(exc))
            messagebox.showerror("Check task details", str(exc), parent=root)
        except StorageError as exc:
            set_status("Task could not be saved")
            messagebox.showerror("Unable to add task", str(exc), parent=root)
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
    complete_button.configure(command=complete_selected_task)
    edit_button.configure(command=edit_selected_task)
    delete_button.configure(command=delete_selected_task)
    search_var.trace_add("write", lambda *_: refresh_task_list())
    filter_combo.bind("<<ComboboxSelected>>", lambda _: refresh_task_list())
    bind_enter_key([date_entry, time_entry, task_entry], add_task)
    root.bind("<Escape>", lambda _event: root.focus_set())
    task_entry.focus_set()
    _center_window(root)
    if startup_notice:
        root.after(
            100,
            lambda: messagebox.showwarning(
                "Database recovered", startup_notice, parent=root
            ),
        )
    root.mainloop()
