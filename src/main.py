"""
main.py
--------
Entry point for SchedPlus

This module creates the `Scheduler`, asks it to load persisted tasks,
and launches the selected UI. UIs interact only with the scheduler API.

Note: No Logic in here, keep it simple!
"""

from startup.controller import boot_full


if __name__ == "__main__":
    raise SystemExit(boot_full())
