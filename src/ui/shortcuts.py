"""
shortcuts.py
-------------------
Keyboard shortcuts and event bindings for SchedPlus UI.

This module handles:
while Tkinter uses these PyQt currently does not.
this will likely not be expanded on to keep UIs independant
"""


def bind_enter_key(fields, event_callback):
    """
    Bind the Enter key to trigger an event on input fields.

    Args:
        fields: List of Entry widgets to bind Enter to
        event_callback: The callback function to execute on Enter

    """
    for field in fields:
        field.bind("<Return>", lambda event: event_callback())
