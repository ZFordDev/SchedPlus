"""Tests for the ReminderService."""

import threading
import time
from datetime import timedelta
from unittest.mock import patch

from logic import local_time
from logic.reminder_service import ReminderService
from logic.scheduler import Task


class MemoryScheduler:
    def __init__(self, tasks=None):
        self.tasks = list(tasks or [])


def test_reset_clears_notified_set():
    scheduler = MemoryScheduler()
    service = ReminderService(scheduler)
    with patch.object(service, "_send_notification"):
        service._notified.add("task-1")
        service._notified.add("task-2")
    service.reset()
    assert service._notified == set()


def test_check_tasks_snapshots_task_list(monkeypatch):
    """Background thread sees a stable snapshot even if main thread mutates."""
    scheduler = MemoryScheduler()
    service = ReminderService(scheduler, poll_interval=1)

    now = local_time.now()
    # remind_at = now - 60s (in window), so task_dt = now - 60s + 10min
    task_dt = now + timedelta(minutes=10) - timedelta(seconds=60)
    task = Task(
        id="task-1",
        date=task_dt.strftime("%Y-%m-%d"),
        time=task_dt.strftime("%H:%M"),
        text="Test",
        reminder="10",
    )
    scheduler.tasks = [task]

    with patch.object(service, "_send_notification") as mock_send:
        service._check_tasks()
        mock_send.assert_called_once_with("Test", task.date, task.time)

    # Mutate original list after check
    scheduler.tasks.append(
        Task(id="task-2", date="2099-01-01", time="00:00", text="Future", reminder="0")
    )

    # Second check should not re-notify task-1
    with patch.object(service, "_send_notification") as mock_send:
        service._check_tasks()
        mock_send.assert_not_called()


def test_notified_cleared_when_reminder_window_passed():
    scheduler = MemoryScheduler()
    service = ReminderService(scheduler)

    # First: task in reminder window (notified added)
    now = local_time.now()
    task_dt = now + timedelta(minutes=10) - timedelta(seconds=60)
    task = Task(
        id="old",
        date=task_dt.strftime("%Y-%m-%d"),
        time=task_dt.strftime("%H:%M"),
        text="Old",
        reminder="10",
    )
    scheduler.tasks = [task]

    with patch.object(service, "_send_notification"):
        service._check_tasks()

    with service._lock:
        assert "old" in service._notified

    # Second check: task moved far into future, diff > 120 -> discard
    far_future = local_time.now() + timedelta(hours=1)
    scheduler.tasks[0] = Task(
        id="old",
        date=far_future.strftime("%Y-%m-%d"),
        time=far_future.strftime("%H:%M"),
        text="Old",
        reminder="10",
    )
    with patch.object(service, "_send_notification"):
        service._check_tasks()

    with service._lock:
        assert "old" not in service._notified


def test_concurrent_notified_access_is_safe():
    """Multiple threads adding/removing from _notified under lock doesn't corrupt."""
    scheduler = MemoryScheduler()
    service = ReminderService(scheduler)
    errors = []

    def worker_add():
        try:
            for i in range(100):
                with service._lock:
                    service._notified.add(f"task-{i}")
                time.sleep(0.0001)
        except Exception as e:  # noqa: BLE001 - surface worker failures to the test
            errors.append(e)

    def worker_remove():
        try:
            for i in range(100):
                with service._lock:
                    service._notified.discard(f"task-{i}")
                time.sleep(0.0001)
        except Exception as e:  # noqa: BLE001 - surface worker failures to the test
            errors.append(e)

    threads = [threading.Thread(target=worker_add) for _ in range(3)] + [
        threading.Thread(target=worker_remove) for _ in range(3)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    with service._lock:
        assert len(service._notified) <= 100


def test_escape_applescript_basic():
    assert ReminderService._escape_applescript("hello") == "hello"
    assert ReminderService._escape_applescript('say "hi"') == 'say \\"hi\\"'
    assert ReminderService._escape_applescript("path\\to\\file") == "path\\\\to\\\\file"
    assert ReminderService._escape_applescript('"\\') == '\\"\\\\'


@patch("logic.reminder_service.subprocess.run")
def test_send_notification_macos_escapes_quotes(mock_run):
    with patch("sys.platform", "darwin"):
        service = ReminderService(MemoryScheduler())
        service._send_notification('Title "quoted"', "2026-08-26", "12:00")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[:2] == ["osascript", "-e"]
        script = args[2]
        assert '\\"' in script
        assert 'Title \\"quoted\\"' in script


@patch("logic.reminder_service.subprocess.run")
def test_send_notification_linux_calls_notify_send(mock_run):
    with patch("sys.platform", "linux"):
        service = ReminderService(MemoryScheduler())
        service._send_notification("Title", "2026-08-26", "12:00")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "notify-send"
        assert args[1] == "--urgency=normal"


@patch("logic.reminder_service.subprocess.run")
def test_send_notification_windows_calls_message_box(mock_run):
    with patch("sys.platform", "win32"):
        service = ReminderService(MemoryScheduler())
        service._send_notification("Title", "2026-08-26", "12:00")
        mock_run.assert_not_called()  # uses ctypes directly


def test_check_tasks_skips_completed_and_no_reminder():
    scheduler = MemoryScheduler()
    service = ReminderService(scheduler)

    now = local_time.now() + timedelta(minutes=10)
    tasks = [
        Task(
            id="1",
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M"),
            text="Done",
            reminder="10",
            completed="true",
        ),
        Task(
            id="2",
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M"),
            text="No reminder",
            reminder="",
        ),
        Task(
            id="3",
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M"),
            text="Zero",
            reminder="0",
        ),
    ]
    scheduler.tasks = tasks

    with patch.object(service, "_send_notification") as mock_send:
        service._check_tasks()
        mock_send.assert_not_called()


def test_check_tasks_notifies_when_in_window():
    scheduler = MemoryScheduler()
    service = ReminderService(scheduler)

    now = local_time.now()
    # remind_at = now - 30s (in window), reminder=10, so task_dt = now - 30s + 10min
    task_dt = now + timedelta(minutes=10) - timedelta(seconds=30)
    task = Task(
        id="notify",
        date=task_dt.strftime("%Y-%m-%d"),
        time=task_dt.strftime("%H:%M"),
        text="Alert",
        reminder="10",
    )
    scheduler.tasks = [task]

    with patch.object(service, "_send_notification") as mock_send:
        service._check_tasks()
        mock_send.assert_called_once_with("Alert", task.date, task.time)
