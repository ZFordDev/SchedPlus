"""
tkinter_ui.py (v0.4)
--------------------
Teaching Tkinter UI for SchedPlus (v0.4).

This UI is intentionally simple and acts as the "teaching" UI.
It interacts only with the `Scheduler` API (no storage paths or
storage module usage). It demonstrates inputs, a task list, and
task addition in a minimal layout.
"""

import tkinter as tk
from tkinter import ttk
from ui.shortcuts import bind_enter_key


def run_ui(scheduler):
    root = tk.Tk()
    root.title("SchedPlus v0.4")

    # --- Input fields ---
    date_label = ttk.Label(root, text="Date (YYYY-MM-DD):")
    date_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    date_entry = ttk.Entry(root)
    date_entry.grid(row=0, column=1, padx=5, pady=5)

    time_label = ttk.Label(root, text="Time (HH:MM):")
    time_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    time_entry = ttk.Entry(root)
    time_entry.grid(row=1, column=1, padx=5, pady=5)

    task_label = ttk.Label(root, text="Task:")
    task_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

    task_entry = ttk.Entry(root, width=40)
    task_entry.grid(row=2, column=1, padx=5, pady=5)

    # --- Task list ---
    task_list = tk.Listbox(root, width=50, height=10)
    task_list.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

    for task in scheduler.get_tasks():
        task_list.insert(tk.END, f"{task.date} {task.time} - {task.text}")

    # --- Add Task button ---
    def add_task():
        date = date_entry.get()
        time = time_entry.get()
        text = task_entry.get()

        if date and time and text:
            scheduler.add_task(date, time, text)

            # Append the newly added task to the listbox
            new_task = scheduler.get_tasks()[-1]
            task_list.insert(tk.END, f"{new_task.date} {new_task.time} - {new_task.text}")

            # Let the scheduler handle persistence (UI does not import storage)
            try:
                scheduler.save_tasks()
            except Exception:
                pass

            # Clear input field
            task_entry.delete(0, tk.END)

    add_button = ttk.Button(root, text="Add Task", command=add_task)
    add_button.grid(row=3, column=0, columnspan=2, pady=5)
    
    bind_enter_key([date_entry, time_entry, task_entry], add_task)
    
    root.mainloop()
