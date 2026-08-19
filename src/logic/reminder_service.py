"""Background reminder service that checks for upcoming tasks and sends notifications."""

import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scheduler import Scheduler


class ReminderService:
    """Polls for tasks due soon and sends native notifications."""

    def __init__(self, scheduler: "Scheduler", poll_interval: int = 60) -> None:
        self._scheduler = scheduler
        self._poll_interval = poll_interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._notified: set[str] = set()

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
        self._notified.clear()

    def _run(self) -> None:
        while self._running:
            try:
                self._check_tasks()
            except Exception:
                pass
            time.sleep(self._poll_interval)

    def _check_tasks(self) -> None:
        now = datetime.now()
        for task in self._scheduler.tasks:
            if task.completed or not task.date or not task.time:
                continue
            try:
                minutes = int(task.reminder)
            except (ValueError, TypeError):
                continue
            if minutes <= 0:
                continue
            try:
                task_dt = datetime.strptime(
                    f"{task.date} {task.time}", "%Y-%m-%d %H:%M"
                )
            except ValueError:
                continue
            remind_at = task_dt - timedelta(minutes=minutes)
            diff = (remind_at - now).total_seconds()
            if -120 <= diff <= 0 and task.id not in self._notified:
                self._send_notification(task.text, task.date, task.time)
                self._notified.add(task.id)
            elif diff > 120:
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
            except Exception:
                pass
        if sys.platform == "darwin":
            try:
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        f'display notification "{body}" with title "{title}"',
                    ],
                    timeout=5,
                    check=False,
                )
                return
            except FileNotFoundError:
                pass
