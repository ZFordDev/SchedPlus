# Changelog

## Unreleased

- Adopted GPL-3.0-only for the complete PyQt desktop distribution and
  Apache-2.0 for the reusable logic layer. The `release-0.7.3` tag remains the
  final blanket-MIT release, with its license and contributor notices retained.
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
- Added native PyQt month, week, and day calendar views with task markers,
  selected-day agendas, timed scheduling grids, navigation, calendar settings,
  and drag-to-reschedule integration with the shared scheduler.
- Fixed PyQt dropdown popup rendering and added clear populated and empty states
  to the month calendar's selected-day agenda panel.
- Replaced the interactive raw CLI with scriptable `add`, `list`, `edit`, and
  `delete` subcommands, UUID-prefix lookup, consistent output, and meaningful
  process exit codes. The previous `--raw` flag remains as a compatibility alias.
- Added the secure self-update foundation for non-Store packages: signed release
  manifests, verified background downloads, external installation handoff,
  atomic managed-install swaps, startup health checks, and last-known-good
  rollback. Source, Snap, and Microsoft Store builds remain opted out.
- Split runtime dependencies into core/CLI, Lite, Standard, and Full profiles.
  Removed unused Babel and direct Qt runtime implementation pins; contributor
  installs retain all interfaces through the development profile.
