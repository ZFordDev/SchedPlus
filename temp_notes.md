> [!NOTE]
> **ZFordDev Standard: Temp Notes**
>
> This file is included in every repository as part of the ZFordDev ecosystem
> standards. It provides a safe local-only space for scratch notes, planning,
> and quick thoughts while working.
>
> This file is ignored by Git (see `.gitignore`) and will never be committed
> or pushed to the repository.

# ***NOTES***

# SchedPlus UI Audit

## Overall summary
SchedPlus currently supports three interactive entry points:
- Tkinter GUI
- PyQt GUI
- Raw CLI

All three use the same scheduler/storage layer underneath, but they differ a lot in how users interact with the app.

## 1) Tkinter GUI
Purpose:
- The most basic and lightweight desktop interface.
- Intended as a simple task-entry form with an embedded task list.

Key characteristics:
- Single-window layout with a form at the top and a task table below.
- Uses standard Tk/Ttk widgets and a small set of helper popups for date/time selection.
- The experience is more direct and minimal, but less polished visually.
- Adding a task is handled inline in the same window.

Strengths:
- Simple to understand and run.
- Lower dependency overhead than PyQt.
- Feels lightweight and familiar for basic desktop usage.

Weaknesses:
- Less modern UI styling.
- Fewer built-in UX patterns such as dialogs, status feedback, and richer layout organization.
- Task presentation is more utilitarian than visually structured.

## 2) PyQt GUI
Purpose:
- The more polished and modern GUI experience.
- Designed as a richer desktop app with better visual hierarchy and interaction flow.

Key characteristics:
- Uses a full-window main application with a styled header, task list area, and a dedicated add-task dialog.
- Tasks are displayed as cards grouped by date, which makes the interface feel more organized.
- Includes a status bar and clearer visual styling, including color, spacing, and hover feedback.
- The add-task flow is separated into a modal dialog instead of using a plain inline form.

Strengths:
- Best overall user experience of the three methods.
- Stronger visual design and structure.
- Better for long-term usability and a more “app-like” feel.

Weaknesses:
- More complex implementation.
- Depends on PyQt, which is heavier than Tkinter.
- Slightly more code to maintain because of the component-based layout.

## 3) Raw CLI
Purpose:
- The terminal-based interaction method.
- Best suited for command-line users, automation, or lightweight usage without a GUI.

Key characteristics:
- No windowed interface at all; everything happens in the terminal.
- Supports interactive prompts for adding tasks, listing tasks, and wiping the database.
- Much more minimal and text-oriented than the GUI options.
- Works well for scripting and quick operations from a shell.

Strengths:
- Extremely lightweight and dependency-light.
- Very portable and easy to use in remote or headless environments.
- Good for quick task management without launching a GUI.

Weaknesses:
- Least user-friendly for non-technical users.
- No visual structure, no rich formatting, and no modern interface affordances.
- More cumbersome for repeated task entry compared to a GUI.

## Direct differences at a glance
- Tkinter is the simplest GUI, focused on a compact form-based experience.
- PyQt is the most polished and feature-rich GUI, with a more modern app layout.
- CLI is the most minimal and text-based option, optimized for terminal usage rather than visual interaction.

## Practical takeaway
If the goal is a polished desktop experience, PyQt is the strongest option. If the goal is simplicity and low overhead, Tkinter is the easiest path. If the goal is speed, scriptability, or terminal-only access, the CLI is the best fit.

# Task and Scheduling Audit

## Overview
The app does not yet have a full scheduling engine in the traditional sense. What it currently has is a lightweight task-management system where each task carries a date, time, and text, and those values are stored and later displayed. In practice, the app is more of a task list with time-based metadata than a true planner or scheduler.

## 1) Task data model
Each task is represented by a Task object with the following fields:
- id: unique identifier for each task
- date: string in YYYY-MM-DD format
- time: string in HH:MM format
- text: the task description/note
- createdAt: timestamp when the task was created
- updatedAt: timestamp when the task was last modified

This model is defined in the scheduler layer and is used consistently across the UI and storage layers.

## 2) How a task is created
The flow for creating a task is:
1. A UI or CLI collects date, time, and text input.
2. The scheduler receives those values via add_task(...).
3. A Task object is created.
4. The task is written into the database through the storage layer.
5. The in-memory task list is updated so the current session reflects the change immediately.

This means task creation is currently simple and synchronous: the input is accepted, persisted, and then visible in the running app.

## 3) How tasks are stored
The app currently uses SQLite as the main persistence layer.
- The database file is stored under the data folder as tasks.db.
- The storage layer creates an entries table with columns for id, date, time, text, createdAt, and updatedAt.
- The scheduler delegates all persistence work to this database layer.

The older JSON-based storage is still part of the project history, but the current flow is SQLite-based.

## 4) How tasks are loaded and displayed
When the app starts:
- the scheduler loads tasks from the database
- the in-memory task list is populated
- each UI then renders whatever is currently loaded

The UI layers do not directly manage persistence; they rely on the scheduler to provide task data.

## 5) How scheduling works today
The current “scheduling” behavior is very basic:
- tasks are associated with a date and time
- tasks are sorted by date and time when read back
- the UI can group or display them by date

There is no deeper scheduling engine for things like:
- recurring tasks
- reminders or alarms
- automatic rescheduling
- priority-based ordering
- conflict detection
- due-soon or overdue logic
- calendar-based planning

So the current app behaves more like a dated to-do list than a full scheduler.

## 6) Update and delete behavior
Tasks are also editable and removable:
- update_task(...) updates the task in the database and refreshes the in-memory list
- delete_task(...) removes the task from the database and removes it from the runtime list

These operations are intentionally simple and do not involve any workflow state or scheduling rules.

## 7) Migration behavior
The app has a migration path from the old JSON file to the new SQLite database:
- if a legacy tasks.json exists and tasks.db does not yet exist, the app will migrate the data automatically
- the legacy JSON file is renamed to a .bak backup after migration

This is an important part of the storage architecture, but it does not change the scheduling model itself.

## 8) Strengths
- Clean separation between task model, scheduler logic, and storage layer
- Persistent storage is present and stable
- The app can load, save, update, and delete tasks reliably
- The UI is decoupled from the persistence details

## 9) Weaknesses and gaps
- Scheduling is effectively just date/time tagging
- No real automation or planning behavior exists yet
- No reminder/notification system
- No recurring task support
- No calendar view or agenda view
- No priority, status, or completion tracking
- The createdAt/updatedAt metadata is stored but not heavily used in the UI

## 10) Bottom line
The app currently functions as a simple dated task manager rather than a true scheduling system. It stores tasks, sorts them by date/time, and presents them to users, but it does not yet implement advanced scheduling features or time-based automation.
