"""
selector.py
-----------
Popup selector window for choosing the UI mode.

Bypass this with direct commands see modes.py
"""

from schedplus.identity import get_application_identity

from .modes import StartupMode

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    tk = None
    ttk = None


class StartupSelector:
    """
    A minimal Tkinter-based popup selector window.
    Returns a StartupMode based on user selection.
    """

    def __init__(self):
        if tk is None:
            raise RuntimeError("Tkinter is not available on this system.")

        self.result = None
        self.identity = get_application_identity()
        self.root = tk.Tk()
        self.root.title(f"{self.identity.version_label} — Select Interface")
        self.root.geometry("300x270")
        self.root.resizable(False, False)

        # Center window
        self.root.eval("tk::PlaceWindow . center")

        # ESC closes
        self.root.bind("<Escape>", lambda e: self._close())

        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Choose Startup Mode", font=("Segoe UI", 12)).pack(
            pady=(0, 10)
        )

        ttk.Button(
            frame, text="Basic | Tkinter", command=lambda: self._select(StartupMode.TK)
        ).pack(fill="x", pady=4)

        ttk.Button(
            frame,
            text="Advanced | PyQt",
            command=lambda: self._select(StartupMode.PYQT),
        ).pack(fill="x", pady=4)

        ttk.Button(
            frame,
            text="Command Line Help",
            command=lambda: self._select(StartupMode.CLI),
        ).pack(fill="x", pady=4)

        ttk.Button(frame, text="Close", command=self._close).pack(
            fill="x", pady=(10, 0)
        )

        ttk.Label(frame, text=self.identity.version_label).pack(pady=(12, 0))

    def _select(self, mode):
        self.result = mode
        self.root.destroy()

    def _close(self):
        self.result = None
        self.root.destroy()

    def show(self) -> StartupMode | None:
        """Show the popup and block until closed."""
        self.root.mainloop()
        return self.result
