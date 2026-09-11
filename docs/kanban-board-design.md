# Kanban board design

Status: **Approved — Session 1 of #192 complete**
Related: #192 (parent), #202 (design), #203 (UI), #204 (drag/drop + undo), #205 (search/a11y)
Applies to: PyQt workspace only (v1.0 scope)

## 1. Purpose

Add a Kanban planning view that complements the existing Tasks and Calendar
views for active planning. It is an **opt-in** surface: a task appears on the
board only when the user deliberately adds it, and each task sits in exactly
one planning stage. Nothing is derived automatically from task fields, and the
board never changes what a task means in Tasks or Calendar.

## 2. Data model

### 2.1 New field

Add `board_stage` to the `Task` dataclass:

```python
board_stage: str = ""   # "" = not on the board; else one of BOARD_STAGES
```

**Decided:** the parent tracking text originally said "nullable `board_stage`
(`NULL` = off-board)". This codebase represents every optional field — `notes`,
`priority`, `duration`, `category`, `recurrence`, `reminder`, `completed` — as
`TEXT NOT NULL DEFAULT ''`, never `NULL`. A `NULL` column would be inconsistent
with every existing field and force guards throughout storage, serialization,
and the UI. Approved approach: store `""` for "not on the board". The semantic
("a task without a stage is not on the board") is unchanged.

### 2.2 Canonical stages

```python
# src/logic/board.py (new module, UI-independent)
BOARD_STAGES = ("backlog", "in_progress", "done")
```

- Values are lowercase, matching `priority` (`low/medium/high`) and
  `recurrence` (`daily/weekly/monthly/yearly`) conventions.
- Display labels are a UI concern: **Backlog**, **In progress**, **Done**.
- No user-defined columns or multiple boards in v1.0 (#192 scope).

### 2.3 Stage vs completion

- A board stage is a planning state, **not** task completion.
- Moving a card to `done` does **not** complete the task.
- Completing a task does **not** move its card.
- A completed task stays in whatever stage it is in until the user moves it.

## 3. Schema migration

Append **migration 7** to `src/logic/storage/migrations.py` (never edit a
released migration):

```python
def _migration_7(connection):
    connection.execute(
        "ALTER TABLE entries ADD COLUMN board_stage TEXT NOT NULL DEFAULT ''"
    )
```

- `CURRENT_SCHEMA_VERSION` becomes 7.
- The existing transactional `migrate_database()` already creates a
  pre-migration backup for existing databases and migrates in order.
- Existing rows get `''` → automatically off-board. **No data is relocated,
  hidden, or duplicated.**

### Storage surface (`src/logic/storage/sqlite_storage.py`)

Add `board_stage` to every SQL statement and row mapping:
`create_entry`, `update_entry`, `get_entry`, `list_entries`,
`list_completed_entries`, `replace_entries`, `import_entries`,
`_task_from_row` (index 15, keep the defensive `if len(row) > 15` guard), and
`_task_values`.

## 4. Validation

Extend `src/logic/validation.py`:

```python
stages = ("backlog", "in_progress", "done")
def validate_board_stage(value: str) -> str:
    value = value.strip()
    if value and value not in stages:
        raise ValidationError(f"Board stage must be one of {', '.join(stages)}.")
    return value
```

- Normalize `" "`/`None`-like emptiness to `""`.
- Reject any value outside `BOARD_STAGES` so the database and UI can never
  disagree about what a valid stage is.
- `validate_task()` calls `validate_board_stage` on `getattr(task,
  "board_stage", "")` so every persistence path is covered.
- Unscheduled (date-less, time-less) tasks are valid for planning; a task with
  only one of date or time set is rejected. The create/edit dialog disables the
  Repeat fields while `Unscheduled` is checked, since a recurring task is
  meaningless without a due date. (Repeat values already present on a dateless
  task are left untouched and ignored.)

## 5. Serialization (backup / restore / export / import)

`src/logic/data_transfer.py`:

- Add `"board_stage"` to the `optional` set in `_parse_tasks`.
- Old files without the key load as `""` (off-board) — backward compatible.
- Export picks the field up automatically via `asdict(task)`.
- `FORMAT_VERSION` stays `1`: the field is additive/optional, exactly like
  `notes`, `category`, and `reminder` were.

## 6. Scheduler

- `Scheduler.add_task(..., board_stage="")` — pass through to `Task`.
- `Scheduler.update_task(task)` — unchanged; it persists the whole object.
- Board moves are ordinary task edits. A move produces a modified `Task` and
  calls `update_task`, so no new scheduler surface is required.

## 7. Undo

No new `UndoAction` type. A board move is recorded with the existing
`UndoManager.record_edit(snapshot_of_task_before_move)`; `Ctrl+Z` runs the
existing `edit` undo path and restores the prior `board_stage` (and any other
fields edited at the same time). This is the same mechanism the edit dialog
already uses (`window.open_edit_dialog`).

## 8. Card content

A card renders the existing task attributes — nothing stored on the card
beyond the task itself:

- text (primary, wraps)
- date + time
- category badge
- priority (styling)
- duration
- recurrence
- reminder
- completion indicator (informational; does not govern board position)

## 9. UI model

### 9.1 Sidebar

Add **Kanban** as a fourth navigation entry in `window.py`:

- `_build_sidebar()`: new `_navigation_button("Kanban")`, consistent with the
  existing Tasks/Calendar/Settings buttons.
- `self.pages.addWidget(board_page)` after the calendar page.
- `show_page("board")` switch in the same `QStackedWidget`.

### 9.2 `BoardView(QWidget)` — new `src/ui/pyqt/board_view.py`

- One column widget per stage, rendered from `scheduler.get_tasks()` grouped
  by `task.board_stage`. Cards are only tasks whose `board_stage` matches.
- Signals mirror `TaskListWidget`: `add_requested`, `edit_requested`,
  `delete_requested`, `complete_requested` — wired in `window.py` to the
  existing handlers (`open_add_dialog`, `open_edit_dialog`, `delete_task`,
  `complete_task`).
- `refresh()` rebuilds from `scheduler.get_tasks()` so board data is always
  the task list itself (Task and Calendar remain the source of truth).
- Empty states: a whole-board empty state and a per-column "no tasks" spill.

### 9.3 Create / edit dialog (`add_dialog.py`)

- Add an **"Add to Kanban"** checkbox (unchecked by default on create).
- When checked, reveal a **Board column** combo (`backlog`, `in_progress`,
  `done`) defaulting to `backlog`.
- On edit, the checkbox is pre-checked when `task.board_stage` is set, and the
  combo preselected. Unchecking clears `board_stage` (removes from board).
- `get_values()` returns `board_stage`; update both callers in `window.py` and
  the affected tests.

### 9.4 Tasks page filter (`task_list.py`, optional for #205)

Add an `On Board` filter option (`task_filter: "board"`) that shows only
tasks with a non-empty `board_stage`. Touches: `FILTERS` in
`settings_dialog.py`, `TaskFilterProxyModel.filterAcceptsRow`, and the
`task_filter` choice set in `data_transfer._validate_ui_preferences`.

### 9.5 Startup view (non-goal for v1.0)

`startup_view` stays `tasks | calendar`. A `board` startup option is possible
later; leaving it out keeps the settings surface unchanged.

## 10. CLI

Keep CLI surface minimal (parent constraint). Recommend only:

```bash
schedplus add "Refactor auth" --date 2026-09-20 --board backlog
schedplus edit 7c94a2 --board done          # also accepts --board "" to remove
```

- Invalid stage exits `2` (existing CLI validation path).
- `list` gains no new filter in v1.0.

## 11. Migration & rollback

- Upgrading adds one column with `''`; the existing pre-migration backup
  mechanism already protects every upgrade.
- Rollback = restore the automatic pre-migration backup (same workflow as any
  schema migration today).
- No data movement, no prompts, no hidden reassignment.

## 12. Non-goals (v1.0)

- User-defined columns; WIP limits; swimlanes; multi-board.
- Auto-derivation of board membership from priority/dates/completion.
- Card ordering within a column beyond stable insertion order.
- Web/online sync of board state.
- Theme/token work for cards (uses existing QSS tokens).

## 13. Test plan

| Area | Coverage |
| --- | --- |
| Schema | Migration 7 runs last; existing migrations 1–6 untouched; `_task_from_row` guards index 15 for pre-7 rows |
| Validation | `""` and each stage accepted; invalid/whitespace-cased values rejected; restored/imported tasks normalized |
| Serialization | Export includes `board_stage`; old import without it loads as `""`; round-trip preserves stage |
| Scheduler | `add_task(board_stage=...)`; `update_task` stage change persists |
| Board model | grouping is UI-independent; off-board tasks excluded |
| Undo | Board move → `Ctrl+Z` restores prior stage |
| PyQt (offscreen) | Sidebar shows Kanban; board lists only opted-in tasks; dialog controls set/clear stage; empty + populated states; `On Board` filter |
| CLI | `--board` on add/edit; invalid stage → exit 2 |

## 14. Files touched (summary)

- `src/logic/scheduler.py` — `Task.board_stage`, `add_task(board_stage=)`.
- `src/logic/board.py` — **new**: `BOARD_STAGES`, grouping helper.
- `src/logic/validation.py` — `validate_board_stage`.
- `src/logic/storage/migrations.py` — migration 7.
- `src/logic/storage/sqlite_storage.py` — column mapping.
- `src/logic/data_transfer.py` — `board_stage` optional field.
- `src/ui/pyqt/board_view.py` — **new**: board page.
- `src/ui/pyqt/window.py` — sidebar entry, wiring, dialog callers.
- `src/ui/pyqt/add_dialog.py` — "Add to Kanban" + column controls.
- `src/ui/pyqt/task_list.py` + `settings_dialog.py` — `On Board` filter.
- `src/cli/commands.py` — `--board` on add/edit.
- `tests/` — new `test_board.py`; updates to schema, data-transfer, CLI,
  PyQt-workspace, and dialog tests.

## 15. Approval checklist (matches #202 acceptance criteria)

- [x] Opt-in model, column set (`backlog`/`in_progress`/`done`), and
      stage-vs-completion semantics approved.
- [x] `""`-instead-of-`NULL` convention confirmed.
- [ ] Serialization, validation, and undo impact specified.
- [ ] Migration keeps existing tasks off-board by default (`''`), no
      duplication, no hidden reassignment.
- [ ] Tasks and Calendar remain the source of truth.

## 16. Delivery model

Kanban work never merges directly to `main`. All sub-issue PRs (#202–#205)
integrate into the parent branch **`feature/kanban-board`**, which is created
off the release point of `main`. When the feature is complete and reviewed,
the maintainer decides to either:

- **integrate**: open a final PR from `feature/kanban-board` into `main`; or
- **cut**: close the parent branch and the sub-issues without merging, leaving
  `main` untouched.

This keeps `main` shippable at any time and lets the feature be reworked or
dropped without touching released code paths.