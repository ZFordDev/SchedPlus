"""
tkinter_ui.py (v0.5 - DB compatible MVP)
----------------------------------------
Minimal compatibility update for the new DB-backed scheduler.

Full UI overhaul will happen in a separate issue.
"""

import tkinter as tk
from tkinter import ttk
from ui.shortcuts import bind_enter_key


def run_ui(scheduler):
    root = tk.Tk()
    root.title("SchedPlus v0.5 (Tkinter)")

    root.geometry("420x420")

    container = ttk.Frame(root, padding=15)
    container.grid(row=0, column=0, sticky="nsew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    heading = ttk.Label(container, text="Add a Task", font=("Segoe UI", 12, "bold"))
    heading.grid(row=0, column=0, columnspan=2, pady=(0, 10))

    ttk.Label(container, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=3)
    date_entry = ttk.Entry(container, width=25)
    date_entry.grid(row=1, column=1, sticky="ew", pady=3)

    ttk.Label(container, text="Time (HH:MM):").grid(row=2, column=0, sticky="w", pady=3)
    time_entry = ttk.Entry(container, width=25)
    time_entry.grid(row=2, column=1, sticky="ew", pady=3)

    ttk.Label(container, text="Task:").grid(row=3, column=0, sticky="w", pady=3)
    task_entry = ttk.Entry(container, width=25)
    task_entry.grid(row=3, column=1, sticky="ew", pady=3)

    add_button = ttk.Button(container, text="Add Task")
    add_button.grid(row=4, column=0, columnspan=2, pady=(10, 15))

    list_frame = ttk.LabelFrame(container, text="Tasks", padding=10)
    list_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")

    container.rowconfigure(5, weight=1)
    list_frame.rowconfigure(0, weight=1)
    list_frame.columnconfigure(0, weight=1)

    task_list = tk.Listbox(list_frame, width=50, height=10, borderwidth=1, relief="solid")
    task_list.grid(row=0, column=0, sticky="nsew")

    # --- Populate tasks from DB ---
    for entry in scheduler.list_tasks():
        # entry.due_date is ISO: "YYYY-MM-DDTHH:MM"
        date, time = _split_due_date(entry.due_date)
        task_list.insert(tk.END, f"{date} {time} - {entry.title}")

    # --- Add Task logic ---
    def add_task():
        date = date_entry.get().strip()
        time = time_entry.get().strip()
        title = task_entry.get().strip()

        if date and time and title:
            due_date = f"{date}T{time}"

            scheduler.add_task(
                title=title,
                description=None,
                due_date=due_date,
            )

            new_entry = scheduler.list_tasks()[-1]
            new_date, new_time = _split_due_date(new_entry.due_date)

            task_list.insert(tk.END, f"{new_date} {new_time} - {new_entry.title}")

            task_entry.delete(0, tk.END)

    add_button.config(command=add_task)
    bind_enter_key([date_entry, time_entry, task_entry], add_task)

    root.mainloop()


def _split_due_date(due_date: str):
    """
    Helper: Convert ISO "YYYY-MM-DDTHH:MM" → ("YYYY-MM-DD", "HH:MM")
    """
    if due_date and "T" in due_date:
        return due_date.split("T", 1)
    return ("", "")
