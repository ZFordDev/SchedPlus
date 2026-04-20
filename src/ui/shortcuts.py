"""
shortcuts.py (v0.1)
-------------------
Keyboard shortcuts and event bindings for SchedPlus UI.

This module handles:
- Enter key binding for quick task addition
- Cross-platform compatibility (Windows, Linux, macOS)

Later versions will:
- Add more keyboard shortcuts
- Add customizable keybindings
"""


def bind_enter_key(fields, event_callback):
    """
    Bind the Enter key to trigger an event on input fields.
    
    Args:
        fields: List of Entry widgets to bind Enter to
        event_callback: The callback function to execute on Enter
    
    Works on Windows, Linux, and macOS.
    """
    for field in fields:
        field.bind("<Return>", lambda event: event_callback())
