# Changelog

## v0.9.1 (2026-08-23)

### Fixed
- `list_completed_entries` now loads all task fields instead of dropping notes, priority, duration, category, recurrence, and reminder [#160]
- Monthly and yearly recurrences clamp to the last valid day of the target month (Jan 31 → Feb 28, Feb 29 → Feb 28) instead of failing silently [#157]
- Replaced deprecated `datetime.utcnow()` in Task defaults while preserving the stored timestamp format [#153]
- Settings no longer show "Check automatically" as enabled for store-managed builds (Snap, MSIX); the preference displays as off and can never be persisted as on [#166]

## v0.9.0 (2026-08-19)

### Plan
- Bring the Lite interface to complete task-management parity [#133]
- Expand the task model with notes, priority, and duration [#134]
- Add categories and local organization [#135]
- Add recurring tasks [#136]
- Add offline reminders and native notifications [#137]
- Add undo and recovery for common task actions [#138]
- Complete settings, About, diagnostics, and data-location controls [#139]
- Perform an accessibility and keyboard-navigation pass [#140]
- Add configurable date, time, and week preferences [#141]
- Complete release documentation and offline privacy guarantees [#142]

### Added
- Task completion tracking with completed/completedAt fields and schema migration [#132]
- Complete/Uncomplete actions in PyQt and Tkinter interfaces [#132]
- "Show completed" toggle in Tkinter UI and "Active"/"Completed" filters in PyQt [#132]
- CLI `complete` command to mark tasks complete/incomplete by ID prefix [#132]
- CLI `list --filter` flag to show all, active, or completed tasks [#132]
- Status column in task table views across all interfaces [#132]
- Edit and delete actions in the Lite (Tkinter) interface [#133]
- Search bar and filter dropdown in the Lite interface task list [#133]
- Task notes, priority (low/medium/high), and duration fields with schema migration [#134]
- Notes, priority, and duration editors in PyQt and Tkinter edit dialogs [#134]
- Task category field for local organization with schema migration [#135]
- Category input in PyQt and Tkinter edit dialogs [#135]
- Recurring tasks (daily/weekly/monthly/yearly) with optional end date and schema migration [#136]
- Auto-generation of next occurrence on task completion for recurring tasks [#136]
- Offline task reminders with native system notifications (Linux/macOS/Windows) [#137]
- Background reminder polling service with configurable lead time per task [#137]
- Undo manager with Ctrl+Z support for add, edit, delete, complete, and reschedule actions [#138]
- Tabbed settings dialog with General, Data, and About sections [#139]
- Data tab showing database path, diagnostics, and "Open folder" action [#139]
- About tab with version, edition, platform, and privacy information [#139]
- Enhanced About dialog with local-first privacy statement [#139]
- Accessible names on all interactive widgets for screen reader support [#140]
- Keyboard shortcuts: Ctrl+Q (quit), Ctrl+Z (undo), F11 (full screen) [#140]
- Keyboard shortcuts reference dialog in Help menu [#140]
- Configurable date format (ISO, US, EU, DE) and time format (24h/12h) in settings [#141]
- Week number toggle in calendar view [#141]
- Format preferences applied to task list, dialogs, and calendar [#141]

### Added (docs)
- PRIVACY.md with offline privacy guarantee and data location details [#142]
- Updated README highlights with v0.9.0 features [#142]
- Local-first privacy statement in README Data and privacy section [#142]

### Fixed
-

## Pre-Release version 0.8.1

- Added a shared application identity provider backed by packaged
  `build-info.json` metadata, with installed package metadata as the version
  fallback.
- Displayed `SchedPlus vX.Y.Z` in the PyQt sidebar, Tkinter footer, and Full
  edition interface selector.
- Added About details for the installed edition, update channel, package
  format, platform, and architecture.
- Added `schedplus --version` to the command-line interface.
- Enabled signed stable and preview update manifests for approved releases,
  with Ed25519 manifest verification and signed SHA-256 artifact metadata.
- Embedded package-aware `build-info.json` metadata in Windows portable and
  installer builds, Debian packages, AppImage, Snap, and Microsoft Store MSIX.
- Added managed Windows portable updates using an independent updater, atomic
  activation, startup health confirmation, and last-known-good rollback.
- Added verified Debian and AppImage download handoff. Standalone Windows
  installer updates remain disabled until public Authenticode signing is
  configured; Microsoft Store MSIX updates remain Store-managed.
- Added manual update checks, automatic-check preferences, and persistent last
  update results to the desktop and command-line interfaces.
- Added an end-to-end upgrade test from v0.8.1 to a signed test release.
- Added ordered, transactional SQLite schema migrations tracked with
  `PRAGMA user_version`, including automatic pre-migration backups and safe
  refusal of databases created by newer SchedPlus versions.
- Added upgrade coverage for databases created by v0.7.3 and v0.8.0, migration
  rollback and ordering tests, and continued corruption-recovery coverage.
- Added offline, versioned JSON backup and restore for tasks and local
  preferences, including validation and an automatic pre-restore safety backup.
- Added portable JSON task export and non-destructive import to PyQt, Lite, and
  CLI, with explicit duplicate and ID-conflict reporting.
- Added post-release fresh-install, populated-database upgrade, uninstall, and
  Store-policy smoke gates for supported Linux and Windows artifacts.
- Added sanitized diagnostic-log artifacts, an all-checks-required stable
  promotion job, and a manual real-host and Store verification checklist.
- Fixed frozen Standard, Lite, Full, and CLI artifacts failing at startup
  because updater modules were not explicitly collected by PyInstaller.
- Fixed MSIX packaging-test collection importing release-only cryptographic
  dependencies before they are needed.

## Pre-Release version 0.8.0
- Added unified tag/version validation, pre-package testing, independent Linux,
  Windows, and Snap builds, exact source archives, release-payload validation,
  unified checksums, an SPDX source SBOM, and draft candidate GitHub Releases.
- Replaced the legacy generated Snap workflow with a committed, strictly
  confined `schedplus` manifest for the Standard PyQt edition, persistent task
  storage, desktop integration, clean-install and refresh checks, staged Store
  channels, and prepared listing copy.
- Added Standard, Lite, Full, and CLI Windows portable ZIP builds and a
  per-user Standard installer with Start Menu integration, uninstallation,
  source disclosures, checksums, and clean-runner lifecycle tests.
- Added a Standard-only Microsoft Store MSIX manifest, Store visual-asset
  generation, manual CI package build, release-listing material, and packaging
  validation. Store publication remains manually controlled.
- Documented v0.8.0 editions, package formats, installation, upgrades,
  data retention, licensing, and source availability in the repository and
  DocsHub guides.
- Added a portable Standard-edition AppImage build with checksum generation,
  extraction fallback testing, and read-only runtime behavior.
- Added release-grade Debian packaging for Standard, Lite, and CLI frozen
  editions, with correct filesystem layout, metadata, licensing, linting, and
  installation/removal validation.
- Added reproducible PyInstaller onedir specifications for Standard, Lite,
  Full, and CLI editions, including frozen artifact validation in CI.
- Store Snap task data under `SNAP_USER_COMMON` so it persists across package
  revisions, with safe normal-Linux fallback when that variable is unavailable.
- Added shared release metadata for the stable `dev.zford.SchedPlus`
  application identity, including Linux desktop and AppStream metadata,
  validated icon assets, a multi-resolution Windows ICO, Store asset guidance,
  and CI validation.
- Updated Debian and Snap release descriptions to use current SchedPlus branding.
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
