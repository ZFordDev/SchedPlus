"""
tkinter_ui.py (v0.5)
--------------------
Improved teaching Tkinter UI for SchedPlus.

Still intentionally simple, but with cleaner layout,
better spacing, and more readable structure.
"""

import tkinter as tk
from tkinter import ttk
from ui.shortcuts import bind_enter_key


def run_ui(scheduler):
    root = tk.Tk()
    root.title("SchedPlus v0.5 (Tkinter)")

    # Center window
    root.geometry("420x420")

    # --- Main container ---
    container = ttk.Frame(root, padding=15)
    container.grid(row=0, column=0, sticky="nsew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # --- Heading ---
    heading = ttk.Label(container, text="Add a Task", font=("Segoe UI", 12, "bold"))
    heading.grid(row=0, column=0, columnspan=2, pady=(0, 10))

    # --- Input fields ---
    ttk.Label(container, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=3)
    date_entry = ttk.Entry(container, width=25)
    date_entry.grid(row=1, column=1, sticky="ew", pady=3)

    ttk.Label(container, text="Time (HH:MM):").grid(row=2, column=0, sticky="w", pady=3)
    time_entry = ttk.Entry(container, width=25)
    time_entry.grid(row=2, column=1, sticky="ew", pady=3)

    ttk.Label(container, text="Task:").grid(row=3, column=0, sticky="w", pady=3)
    task_entry = ttk.Entry(container, width=25)
    task_entry.grid(row=3, column=1, sticky="ew", pady=3)

    # --- Add Task button ---
    add_button = ttk.Button(container, text="Add Task")
    add_button.grid(row=4, column=0, columnspan=2, pady=(10, 15))

    # --- Task list frame ---
    list_frame = ttk.LabelFrame(container, text="Tasks", padding=10)
    list_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")

    container.rowconfigure(5, weight=1)
    list_frame.rowconfigure(0, weight=1)
    list_frame.columnconfigure(0, weight=1)

    # --- Task list ---
    task_list = tk.Listbox(list_frame, width=50, height=10, borderwidth=1, relief="solid")
    task_list.grid(row=0, column=0, sticky="nsew")

    # Populate existing tasks
    for task in scheduler.get_tasks():
        task_list.insert(tk.END, f"{task.date} {task.time} - {task.text}")

    # --- Add Task logic ---
    def add_task():
        date = date_entry.get().strip()
        time = time_entry.get().strip()
        text = task_entry.get().strip()

        if date and time and text:
            scheduler.add_task(date, time, text)
            new_task = scheduler.get_tasks()[-1]

            task_list.insert(tk.END, f"{new_task.date} {new_task.time} - {new_task.text}")

            try:
                scheduler.save_tasks()
            except Exception:
                pass

            task_entry.delete(0, tk.END)

    add_button.config(command=add_task)
    bind_enter_key([date_entry, time_entry, task_entry], add_task)

    root.mainloop()
