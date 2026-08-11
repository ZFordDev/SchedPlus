# Changelog

## Unreleased

- Moved the SQLite database to the platform-specific user data directory and
  added automatic relocation of databases created by earlier releases.
- Removed the obsolete JSON persistence backend and migration fallback. SQLite
  is now the sole task storage system.
- Refreshed the lightweight Tkinter interface with a responsive layout,
  friendlier date and time entry, task counts, and visible status feedback.
- Added automatic SQLite initialization and corruption recovery, structured
  storage errors, rotating logs, and interface-specific failure messages.
- Removed the non-functional `--dev` startup flag and its misleading help text.
- Added scheduler-level task validation so every interface enforces normalized
  ISO dates, 24-hour times, and non-empty task text before persistence.
- Expanded PyQt into a maximized advanced workspace with complete task CRUD,
  search, filtering, sorting, shortcuts, persistent preferences, and a native
  calendar navigation foundation.
