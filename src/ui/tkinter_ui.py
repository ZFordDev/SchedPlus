"""
tkinter_ui.py
--------------------
Still intentionally simple, but with cleaner layout,
better spacing, and more readable structure.

This is now User frendly :)
"""

import tkinter as tk
from tkinter import ttk
from ui.shortcuts import bind_enter_key
from tkcalendar import Calendar
from logic.scheduler import Scheduler, Task
from sys import path


def run_ui(scheduler: Scheduler) -> None:
    root = tk.Tk()
    root.title("SchedPlus - Basic")

    # Window sizing
    root.geometry("530x480")
    root.minsize(420, 420)
    root.resizable(True, True)

    # --- Main container ---
    container = ttk.Frame(root, padding=15)
    container.grid(row=0, column=0, sticky="nsew")

    container.columnconfigure(1, weight=1)
    container.columnconfigure(2, weight=0)
    root.rowconfigure(0, weight=1)

    # --- Heading ---
    ttk.Label(container, text="Add a Task", font=("Segoe UI", 12, "bold")).grid(
        row=0, column=0, columnspan=3, pady=(0, 10)
    )

    # --- Date ---
    ttk.Label(container, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=3)
    date_entry = ttk.Entry(container)
    date_entry.grid(row=1, column=1, sticky="ew", pady=3)

    def open_calendar(): # new: still not forcing users to use it
        top = tk.Toplevel(root)
        top.title("Select Date")

        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(padx=10, pady=10)

        def choose():
            date_entry.delete(0, tk.END)
            date_entry.insert(0, cal.get_date())
            top.destroy()

        ttk.Button(top, text="Select", command=choose).pack(pady=5)

    ttk.Button(container, text="📅", width=3, command=open_calendar).grid(
        row=1, column=2, padx=(5, 0)
    )

    # --- Time ---
    ttk.Label(container, text="Time (HH:MM):").grid(row=2, column=0, sticky="w", pady=3)
    time_entry = ttk.Entry(container)
    time_entry.grid(row=2, column=1, sticky="ew", pady=3)

    def open_time_picker(): # new: still not forcing users to use it
        top = tk.Toplevel(root)
        top.title("Select Time")

        frame = ttk.Frame(top, padding=10)
        frame.grid(row=1, column=1)

        ttk.Label(frame, text="Hour:").grid(row=0, column=0, padx=5, pady=5)
        hour_spin = ttk.Spinbox(frame, from_=0, to=23, width=3, format="%02.0f")
        hour_spin.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Minute:").grid(row=1, column=0, padx=5, pady=5)
        minute_spin = ttk.Spinbox(frame, from_=0, to=59, width=3, format="%02.0f")
        minute_spin.grid(row=1, column=1, padx=5, pady=5)

        def choose():
            time_entry.delete(0, tk.END)
            time_entry.insert(0, f"{hour_spin.get()}:{minute_spin.get()}")
            top.destroy()

        ttk.Button(top, text="Select", command=choose).grid(row=1, column=0, pady=10)

    ttk.Button(container, text="🕒", width=3, command=open_time_picker).grid(
        row=2, column=2, padx=(5, 0)
    )

    # --- Task text ---
    ttk.Label(container, text="Task:").grid(row=3, column=0, sticky="w", pady=3)
    task_entry = ttk.Entry(container)
    task_entry.grid(row=3, column=1, sticky="ew", pady=3)

    # --- Add Task button ---
    add_button = ttk.Button(container, text="Add Task")
    add_button.grid(row=4, column=0, columnspan=3, pady=(10, 15))

    # --- Task list ---
    list_frame = ttk.LabelFrame(container, text="Tasks", padding=10)
    list_frame.grid(row=5, column=0, columnspan=3, sticky="nsew")

     # --- Task list (Treeview) ---
    columns = ("date", "time", "text")

    task_list = ttk.Treeview(
        list_frame,
        columns=columns,
        show="headings",
        height=10
    )

    # Column headings
    task_list.heading("date", text="Date")
    task_list.heading("time", text="Time")
    task_list.heading("text", text="Task")

    # Column widths
    task_list.column("date", width=100, anchor="center")   # YYYY-MM-DD
    task_list.column("time", width=60, anchor="center")    # HH:MM
    task_list.column("text", width=300, anchor="w")        # expands

    task_list.grid(row=0, column=0, sticky="nsew")

    # Scrollbar
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=task_list.yview)
    task_list.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky="ns")


    for task in scheduler.get_tasks():  # type: Task
        task_list.insert("", "end", values=(task.date, task.time, task.text))

    # --- Add Task logic ---
    def add_task():
        date = date_entry.get().strip()
        time = time_entry.get().strip()
        text = task_entry.get().strip()

        if date and time and text:
            scheduler.add_task(date, time, text)
            new_task = scheduler.get_tasks()[-1]
            task_list.insert("", "end", values=(new_task.date, new_task.time, new_task.text))

            try:
                scheduler.save_tasks()
                print("Saving to:", filepath)
            except Exception:
                pass

            task_entry.delete(0, tk.END)

    add_button.config(command=add_task)
    bind_enter_key([date_entry, time_entry, task_entry], add_task)

    root.mainloop()
