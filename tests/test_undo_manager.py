from logic.undo_manager import UndoManager


class RecordingScheduler:
    def __init__(self):
        self.deleted = []

    def delete_task(self, task_id):
        self.deleted.append(task_id)


class FailingScheduler:
    def delete_task(self, _task_id):
        raise RuntimeError("storage unavailable")


def test_successful_undo_consumes_action():
    scheduler = RecordingScheduler()
    manager = UndoManager(scheduler)
    manager.record_add("task-1")

    assert manager.undo() == "Undid add"
    assert scheduler.deleted == ["task-1"]
    assert not manager.can_undo()


def test_failed_undo_is_logged_and_remains_available(caplog):
    manager = UndoManager(FailingScheduler())
    manager.record_add("task-1")

    with caplog.at_level("ERROR"):
        assert manager.undo() is None

    assert manager.can_undo()
    assert "Unable to undo add action" in caplog.text
