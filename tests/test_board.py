import pytest

from logic.board import BOARD_STAGES, group_by_stage
from logic.scheduler import Scheduler, Task
from logic.storage import sqlite_storage as storage


@pytest.fixture
def database(monkeypatch, tmp_path):
    path = tmp_path / "data" / "tasks.db"
    path.parent.mkdir()
    monkeypatch.setattr(storage, "prepare_database", lambda: path)
    monkeypatch.setattr(storage, "_configure_logging", lambda _directory: None)
    return path


def test_board_stages_are_canonical():
    assert BOARD_STAGES == ("backlog", "in_progress", "done")


def test_group_by_stage_excludes_off_board_tasks():
    tasks = [
        Task(
            date="2026-09-11", time="09:00", text="Backlog item", board_stage="backlog"
        ),
        Task(
            date="2026-09-12", time="10:00", text="Doing it", board_stage="in_progress"
        ),
        Task(date="2026-09-13", time="11:00", text="Shipped", board_stage="done"),
        Task(date="2026-09-14", time="12:00", text="Not on the board"),
    ]

    grouped = group_by_stage(tasks)

    assert grouped == {
        "backlog": [tasks[0]],
        "in_progress": [tasks[1]],
        "done": [tasks[2]],
    }


def test_group_by_stage_always_returns_every_stage():
    grouped = group_by_stage([Task(text="Anything")])

    assert set(grouped) == set(BOARD_STAGES)
    assert all(grouped[stage] == [] for stage in BOARD_STAGES)


def test_group_by_stage_preserves_stable_insertion_order():
    text = [Task(text=f"Card {index}", board_stage="backlog") for index in range(3)]

    assert [task.text for task in group_by_stage(text)["backlog"]] == [
        "Card 0",
        "Card 1",
        "Card 2",
    ]


def test_add_task_persists_board_stage(database):
    storage.initialize_database()
    scheduler = Scheduler()

    scheduler.add_task("2026-09-11", "09:00", "Plan release", board_stage="in_progress")

    assert scheduler.load_tasks()[0].board_stage == "in_progress"


def test_unscheduled_task_roundtrips_without_date(database):
    storage.initialize_database()
    scheduler = Scheduler()

    task = scheduler.add_task("", "", "Brainstorm ideas", board_stage="backlog")

    persisted = scheduler.load_tasks()[0]
    assert persisted.id == task.id
    assert (persisted.date, persisted.time) == ("", "")
    assert persisted.board_stage == "backlog"


def test_update_task_changes_and_clears_board_stage(database):
    storage.initialize_database()
    scheduler = Scheduler()
    task = scheduler.add_task(
        "2026-09-11", "09:00", "Plan release", board_stage="backlog"
    )

    moved = Task(
        id=task.id,
        date=task.date,
        time=task.time,
        text=task.text,
        createdAt=task.createdAt,
        updatedAt=task.updatedAt,
        board_stage="done",
    )
    scheduler.update_task(moved)
    assert scheduler.load_tasks()[0].board_stage == "done"

    cleared = Task(
        id=task.id,
        date=task.date,
        time=task.time,
        text=task.text,
        createdAt=task.createdAt,
        updatedAt=task.updatedAt,
        board_stage="",
    )
    scheduler.update_task(cleared)
    assert scheduler.load_tasks()[0].board_stage == ""


def test_undo_restores_prior_board_stage(database):
    storage.initialize_database()
    scheduler = Scheduler()
    task = scheduler.add_task(
        "2026-09-11", "09:00", "Plan release", board_stage="backlog"
    )
    moved = Task(
        id=task.id,
        date=task.date,
        time=task.time,
        text=task.text,
        createdAt=task.createdAt,
        updatedAt=task.updatedAt,
        board_stage="done",
    )

    scheduler.undo_manager.record_edit(task)
    scheduler.update_task(moved)
    scheduler.undo_manager.undo()

    assert scheduler.load_tasks()[0].board_stage == "backlog"
