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
