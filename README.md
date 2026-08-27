<div align="center">

# SchedPlus

### A modern, local-first scheduler for Windows and Linux

[Website](https://schedplus.app/) · [Documentation](https://docs.zford.dev/schedplus/) · [Downloads](https://github.com/ZFordDev/SchedPlus/releases) · [Report a bug](https://github.com/ZFordDev/SchedPlus/issues/new/choose)

[![Status](https://img.shields.io/badge/status-active-4CAF50?style=flat-square)](https://github.com/ZFordDev/SchedPlus)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-0078D4?style=flat-square)](https://docs.zford.dev/schedplus/packaging-guide/)
[![GitHub downloads](https://img.shields.io/github/downloads/ZFordDev/SchedPlus/total?style=flat-square)](https://github.com/ZFordDev/SchedPlus/releases)
[![Desktop license: GPL-3.0](https://img.shields.io/badge/desktop-GPL--3.0-blue?style=flat-square)](LICENSE)
[![Core license: Apache-2.0](https://img.shields.io/badge/core-Apache--2.0-D22128?style=flat-square)](LICENSES/Apache-2.0.txt)

</div>

SchedPlus is a focused desktop application for organising tasks and planning
time without requiring an account or constant network connection. Task data is
stored locally, and backup, restore, import, and export remain under the user's
control.

<p align="center">
  <img src="assets/screenshots/schedplus-tkinter.png" width="48%" alt="SchedPlus Lite interface" />
  <img src="assets/screenshots/schedplus-pyqt.png" width="48%" alt="SchedPlus Standard interface" />
</p>

## Highlights

- Create, edit, delete, search, filter, and sort scheduled tasks.
- Plan through native month, week, and day calendar views.
- Create tasks from the calendar and drag them to reschedule.
- Choose the advanced PyQt workspace, lightweight Tkinter interface, or CLI.
- Keep task data in a platform-appropriate local SQLite database.
- Create versioned local backups and portable JSON task exports.
- Upgrade through signed, package-aware release metadata where supported.
- Recover from failed schema migrations, damaged databases, and managed
  portable-update failures.
- Track task completion history with undo support for all common actions.
- Organize tasks with notes, priority levels, duration estimates, and categories.
- Set recurring tasks (daily, weekly, monthly, yearly) with optional end dates.
- Receive offline reminders via native system notifications.
- Configure date/time formats, week numbers, and accessibility preferences.

SchedPlus is offline-first. Future online accounts, synchronization, web, and
mobile capabilities are planned as optional additions rather than requirements
for local task management.

## Editions

| Edition | Best for | Interface |
| --- | --- | --- |
| **Standard** | Recommended desktop experience | Advanced PyQt workspace |
| **Lite** | A smaller, focused desktop workflow | Tkinter interface |
| **Full** | Choosing either desktop interface | Interface selector |
| **CLI** | Terminals, scripts, and automation | Command line |

Packaged releases are available as Debian packages, an AppImage, a Windows
installer, Windows portable ZIPs, a strict-confinement Snap, and a Microsoft
Store package. Snap and Microsoft Store installations receive Store-managed
updates.

See the [installation guide](https://docs.zford.dev/schedplus/packaging-guide/)
for current package choices, checksums, platform instructions, upgrade policy,
and data-retention behavior.

## Quick start from source

Python 3.10 or later is required for source installations.

```bash
git clone https://github.com/ZFordDev/SchedPlus.git
cd SchedPlus
python -m venv .venv
source .venv/bin/activate
pip install -e ".[full]"
schedplus
```

On Windows, activate with `.venv\Scripts\Activate.ps1`. Some Linux systems
also require the operating-system `python3-tk` package for Lite.

Available development profiles are `lite`, `standard`, `full`, and `dev`.
Contributor setup and project conventions are documented in
[CONTRIBUTING.md](CONTRIBUTING.md).

## Command-line example

```bash
schedplus add "Buy milk" --date 2026-08-20 --time 14:00
schedplus list
schedplus backup SchedPlus-backup.json
schedplus export SchedPlus-tasks.json
```

Run `schedplus --help` or see the
[CLI reference](https://docs.zford.dev/schedplus/cli-reference/) for
editing, deletion, restore, import, update, sorting, and exit-code details.

## Data and privacy

SchedPlus is a local-first application. In current releases, task data, backups,
and preferences are stored on your device and are not uploaded or synchronized.
Supported packages may contact GitHub for signed update metadata and verified
downloads; Store packages use their provider's update service.

SchedPlus does not store tasks inside its installation directory. Package
upgrades and ordinary uninstallation retain the user data directory. The
desktop **Data** menu and CLI provide local backup, restore, export, and import.
Nothing in those operations is uploaded by SchedPlus.

For the complete privacy policy, see [PRIVACY.md](PRIVACY.md).

Snap and Microsoft Store packages use Store-managed updates. Supported Debian,
AppImage, and Windows portable builds verify signed update metadata and artifact
checksums before presenting or installing an update. Update failures never
prevent application startup.

For exact data locations, migration behavior, backup formats, updater policy,
and offline privacy guarantees, use the
[SchedPlus documentation](https://docs.zford.dev/schedplus/).

## Documentation

- [Getting started](https://docs.zford.dev/schedplus/getting-started/)
- [Desktop guide](https://docs.zford.dev/schedplus/desktop-guide/)
- [CLI reference](https://docs.zford.dev/schedplus/cli-reference/)
- [Installation and packages](https://docs.zford.dev/schedplus/packaging-guide/)
- [Technical overview](https://docs.zford.dev/schedplus/technical-overview/)
- [Troubleshooting](https://docs.zford.dev/schedplus/troubleshooting/)
- [Release history](CHANGELOG.md)

## Project status

SchedPlus is under active development. The current roadmap completes the
offline task-management experience before the 1.0 visual launch; optional
online services follow after the local product is dependable and complete.

Track current work through the [issue tracker](https://github.com/ZFordDev/SchedPlus/issues)
and [release notes](https://github.com/ZFordDev/SchedPlus/releases).

## Support and contributing

Bug reports, feature ideas, documentation improvements, and code contributions
are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.
Report security vulnerabilities through [SECURITY.md](SECURITY.md), not a
public issue.

## License

The complete desktop application is distributed under
[GPL-3.0-only](LICENSE). Reusable core modules under `src/logic` are also
available under the [Apache License 2.0](LICENSES/Apache-2.0.txt). Third-party
dependencies retain their respective licenses. See [NOTICE](NOTICE) for the
licensing boundary and historical attribution.
