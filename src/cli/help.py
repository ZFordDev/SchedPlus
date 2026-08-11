"""Concise startup help shown for an unknown top-level option."""


def show_startup_help():
    print(
        """Usage: schedplus [--tk | --py] | COMMAND [OPTIONS]

Interfaces:
  --tk                 Launch the lightweight Tkinter interface
  --py                 Launch the advanced PyQt interface
  (no arguments)       Show the interface selector

Task commands:
  add                  Create a task
  list                 List tasks
  edit                 Edit a task by ID or ID prefix
  delete               Delete a task by ID or ID prefix

Run 'schedplus --help' for command help or
'schedplus COMMAND --help' for command-specific options."""
    )


def show_general_help():
    show_startup_help()
