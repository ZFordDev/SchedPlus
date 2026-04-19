"""
tkinter_ui.py (v0.1)
--------------------
This is the first version of the Tkinter UI.

It provides:
- A window
- Date input
- Time input
- Task text input
- Add Task button
- A listbox to display tasks

Later versions will:
- Improve layout
- Add validation
- Add save/load
- Add PyQt alternative UI
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


def run_ui(scheduler):
    root = tk.Tk()
    root.title("SchedPlus v0.1")

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

    # --- Add Task button ---
     # --- Add Task button ---
    def add_task():
        date = date_entry.get().strip()
        time = time_entry.get().strip()
        text = task_entry.get().strip()

        # Check empty fields
        if not date or not time or not text:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        # Validate date and time format
        if not validate_datetime(date, time):
            messagebox.showerror(
                "Invalid Format",
                "Date must be YYYY-MM-DD\nTime must be HH:MM (24-hour format)"
            )
            return

        # If valid → add task
        scheduler.add_task(date, time, text)
        task_list.insert(tk.END, f"{date} {time} - {text}")

        # Clear fields
        date_entry.delete(0, tk.END)
        time_entry.delete(0, tk.END)
        task_entry.delete(0, tk.END)

    add_button = ttk.Button(root, text="Add Task", command=add_task)
    add_button.grid(row=3, column=0, columnspan=2, pady=5)

    root.mainloop()
    
