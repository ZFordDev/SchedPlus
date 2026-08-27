"""Background reminder service that checks for upcoming tasks and sends notifications."""

import logging
import subprocess
import sys
import threading
import time
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scheduler import Scheduler

from . import local_time

LOGGER = logging.getLogger(__name__)


class ReminderService:
    """Polls for tasks due soon and sends native notifications."""

    def __init__(self, scheduler: "Scheduler", poll_interval: int = 60) -> None:
        self._scheduler = scheduler
        self._poll_interval = poll_interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._notified: set[str] = set()
        self._lock = threading.Lock()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def reset(self) -> None:
        with self._lock:
            self._notified.clear()

    def _run(self) -> None:
        while self._running:
            try:
                self._check_tasks()
            except Exception:  # noqa: BLE001 - keep the background service alive
                LOGGER.exception("Reminder check failed")
            time.sleep(self._poll_interval)

    def _check_tasks(self) -> None:
        now = local_time.now()
        tasks = list(self._scheduler.tasks)
        for task in tasks:
            if task.completed or not task.date or not task.time:
                continue
            try:
                minutes = int(task.reminder)
            except (ValueError, TypeError):
                continue
            if minutes <= 0:
                continue
            try:
                task_dt = local_time.combine(task.date, task.time)
            except ValueError:
                continue
            remind_at = task_dt - timedelta(minutes=minutes)
            diff = (remind_at - now).total_seconds()
            with self._lock:
                notified = task.id in self._notified
            if -120 <= diff <= 0 and not notified:
                self._send_notification(task.text, task.date, task.time)
                with self._lock:
                    self._notified.add(task.id)
            if diff > 120:
                with self._lock:
                    self._notified.discard(task.id)

    def _send_notification(self, title: str, date: str, time: str) -> None:
        body = f"Due at {time} on {date}"
        if sys.platform == "linux":
            try:
                subprocess.run(
                    ["notify-send", "--urgency=normal", title, body],
                    timeout=5,
                    check=False,
                )
                return
            except FileNotFoundError:
                pass
        if sys.platform == "win32":
            try:
                from ctypes import windll

                windll.user32.MessageBoxW(0, body, f"Reminder: {title}", 0x40 | 0x1000)
                return
            except (AttributeError, OSError):
                LOGGER.exception("Windows reminder notification failed")
        if sys.platform == "darwin":
            try:
                script = f'display notification "{self._escape_applescript(body)}" with title "{self._escape_applescript(title)}"'
                subprocess.run(
                    ["osascript", "-e", script],
                    timeout=5,
                    check=False,
                )
                return
            except FileNotFoundError:
                pass

    @staticmethod
    def _escape_applescript(text: str) -> str:
        """Escape string for safe interpolation into AppleScript double-quoted string."""
        return text.replace("\\", "\\\\").replace('"', '\\"')
