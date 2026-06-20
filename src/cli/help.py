"""
help.py
-------
Centralized help system for SchedPlus. 
NEW: colored CLI help output.
"""

# ANSI colors
C_RESET = "\033[0m"
C_HEADER = "\033[95m"
C_CMD = "\033[96m"
C_DESC = "\033[90m"
C_WARN = "\033[91m"

def _fmt(cmd, desc): # Format a command/description pair with alignment.
    return f"  {C_CMD}{cmd:<18}{C_RESET} {C_DESC}{desc}{C_RESET}"

# ---------------------------------------------------------
# STARTUP HELP
# ---------------------------------------------------------

def show_startup_help():
    print(f"""
{C_HEADER}SchedPlus Startup Flags{C_RESET}

{_fmt('--tk', 'Launch Tkinter UI')}
{_fmt('--py', 'Launch PyQt UI')}
{_fmt('--dev', 'Developer mode')}
{_fmt('--raw', 'Use RAW CLI mode')}

(no flags)   Show GUI startup selector
""".rstrip())

# ---------------------------------------------------------
# RAW CLI HELP
# ---------------------------------------------------------

def show_raw_help():
    print(f"""
{C_HEADER}SchedPlus RAW CLI Commands{C_RESET}

{_fmt('schedplus --raw add', 'Add a task (interactive prompts)')}
{_fmt('schedplus --raw list', 'List all tasks')}
{_fmt('schedplus --raw --wipe', 'Wipe ALL tasks (3 confirmations)')}
{_fmt('schedplus --raw help', 'Show this help message')}

{C_DESC}Notes:{C_RESET}
  - Type 'cancel' during add to abort
  - RAW mode is one-shot: command → action → exit
""".rstrip())

# ---------------------------------------------------------
# GENERAL HELP
# ---------------------------------------------------------

def show_general_help():
    print(f"""
{C_HEADER}SchedPlus Help{C_RESET}

{C_HEADER}Startup Modes:{C_RESET}
{_fmt('--tk', 'Launch Tkinter UI')}
{_fmt('--py', 'Launch PyQt UI')}
{_fmt('--dev', 'Developer mode')}
{_fmt('--raw', 'Use RAW CLI mode')}
(no flags)   Show GUI startup selector

{C_HEADER}RAW CLI Commands:{C_RESET}
{_fmt('schedplus --raw add', 'Add a task')}
{_fmt('schedplus --raw list', 'List all tasks')}
{_fmt('schedplus --raw --wipe', 'Wipe all tasks')}
{_fmt('schedplus --raw help', 'Show RAW help')}

Tip:
  Use {C_CMD}schedplus --raw help{C_RESET} for CLI-specific commands.
""".rstrip())
# we can expand this more later