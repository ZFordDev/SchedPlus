from enum import Enum, auto

class StartupMode(Enum):
    POPUP = auto()     # No flags → show GUI selector
    PYQT = auto()      # --py → launch PyQt UI
    TK = auto()        # --tk → launch Tkinter UI
    CLI = auto()       # direct command or legacy --raw alias
    INVALID = auto()   # Invalid flag → show help
