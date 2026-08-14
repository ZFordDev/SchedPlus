# Changelog

## Unreleased (v0.8.1)

### Added

- Added a shared application identity provider backed by packaged
  `build-info.json` metadata, with installed package metadata as the version
  fallback.
- Displayed `SchedPlus vX.Y.Z` in the PyQt sidebar, Tkinter footer, and Full
  edition interface selector.
- Added About details for the installed edition, update channel, package
  format, platform, and architecture.
- Added `schedplus --version` to the command-line interface.

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
