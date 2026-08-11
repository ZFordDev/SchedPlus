import pytest

from ui.validation import add_validated_task, validate_task_input


class RecordingScheduler:
    def __init__(self):
        self.calls = []

    def add_task(self, date, time, text):
        self.calls.append((date, time, text))
        return "created task"


def test_validate_task_input_accepts_and_strips_valid_values():
    assert validate_task_input(" 2026-08-12 ", " 09:05 ", " Plan release ") == (
        "2026-08-12",
        "09:05",
        "Plan release",
    )


@pytest.mark.parametrize("date", ["", "12-08-2026", "2026-8-12", "2026-02-30"])
def test_validate_task_input_rejects_invalid_dates(date):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_task_input(date, "09:05", "Plan release")


@pytest.mark.parametrize("time", ["", "9:05", "09.05", "24:00", "12:60"])
def test_validate_task_input_rejects_invalid_times(time):
    with pytest.raises(ValueError, match="HH:MM"):
        validate_task_input("2026-08-12", time, "Plan release")


@pytest.mark.parametrize("text", ["", "   ", "\t\n"])
def test_validate_task_input_rejects_empty_text(text):
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_task_input("2026-08-12", "09:05", text)


def test_add_validated_task_persists_valid_input():
    scheduler = RecordingScheduler()

    result = add_validated_task(
        scheduler, " 2026-08-12 ", " 09:05 ", " Plan release "
    )

    assert result == "created task"
    assert scheduler.calls == [("2026-08-12", "09:05", "Plan release")]


def test_add_validated_task_does_not_persist_invalid_input():
    scheduler = RecordingScheduler()

    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        add_validated_task(scheduler, "2026-02-30", "09:05", "Plan release")

    assert scheduler.calls == []
