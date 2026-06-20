"""
main.py (v0.4)
--------------
Entry point for SchedPlus (v0.4).

This module creates the `Scheduler`, asks it to load persisted tasks,
and launches the selected UI. UIs interact only with the scheduler API.
"""

from startup.controller import boot


if __name__ == "__main__":
    boot()
