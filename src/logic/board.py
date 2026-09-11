# SPDX-License-Identifier: Apache-2.0

"""UI-independent Kanban board model for SchedPlus."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scheduler import Task

BOARD_STAGES: tuple[str, ...] = ("backlog", "in_progress", "done")


def group_by_stage(tasks: list[Task]) -> dict[str, list[Task]]:
    """Group opted-in tasks by stage; off-board tasks are excluded."""
    staged: dict[str, list[Task]] = {stage: [] for stage in BOARD_STAGES}
    for task in tasks:
        if task.board_stage in staged:
            staged[task.board_stage].append(task)
    return staged
