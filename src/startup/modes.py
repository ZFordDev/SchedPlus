from enum import Enum, auto

class StartupMode(Enum):
    POPUP = auto()     # No flags → show GUI selector
    DEV = auto()       # --dev → terminal selector
    PYQT = auto()      # --py → launch PyQt UI
    TK = auto()        # --tk → launch Tkinter UI
    RAW = auto()       # --raw → reserved for future
    INVALID = auto()   # Invalid flag → show help
