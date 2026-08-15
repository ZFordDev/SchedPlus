<div align="center">

# SchedPlus

### A modern, local-first scheduler for Windows and Linux

[Documentation](https://docs.zford.dev/zforddev/schedplus/) · [Downloads](https://github.com/ZFordDev/SchedPlus/releases) · [Report a bug](https://github.com/ZFordDev/SchedPlus/issues/new/choose)

[![Status](https://img.shields.io/badge/status-active-4CAF50?style=flat-square)](https://github.com/ZFordDev/SchedPlus)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-0078D4?style=flat-square)](#installation)
[![GitHub downloads](https://img.shields.io/github/downloads/ZFordDev/SchedPlus/total?style=flat-square)](https://github.com/ZFordDev/SchedPlus/releases)
[![Desktop license: GPL-3.0](https://img.shields.io/badge/desktop-GPL--3.0-blue?style=flat-square)](LICENSE)
[![Core license: Apache-2.0](https://img.shields.io/badge/core-Apache--2.0-D22128?style=flat-square)](LICENSES/Apache-2.0.txt)

</div>

SchedPlus gives you a focused place to organise tasks and plan your time without unnecessary friction. It is local-first, offline-friendly, and growing into a broader scheduling platform with calendars, reminders, syncing, and accounts on the roadmap.

<p align="center">
  <img src="assets/screenshots/schedplus-tkinter.png" width="48%" alt="SchedPlus Tkinter interface" />
  <img src="assets/screenshots/schedplus-pyqt.png" width="48%" alt="SchedPlus PyQt interface" />
</p>

## Features

- **Local task management** for creating, viewing, updating, and deleting scheduled tasks
- **Native calendar workspace** with month, week, and day planning views
- **Calendar scheduling** with click-to-create, task editing, and drag-to-reschedule workflows
- **SQLite persistence** stored in the platform-appropriate user data directory
- **Offline-friendly workflow** with task data kept on your computer
- **Multiple interfaces** including lightweight Tkinter, the advanced PyQt task workspace, and a scriptable CLI
- **Consistent package identity** showing the installed version, edition, and update channel without reading project files at runtime
- **Cross-platform foundation** targeting Windows and Linux
- **Shared scheduling core** that keeps persistence and interface code separated

## Editions and installation

**Standard** is the recommended edition. It launches the advanced PyQt desktop
workspace directly. **Lite** provides the lightweight Tkinter interface,
**Full** offers an interface selector for source and portable use, and **CLI**
is for terminals and automation.

Download packaged releases from the [GitHub Releases page](https://github.com/ZFordDev/SchedPlus/releases).
Always verify the matching SHA-256 checksum before running a downloaded file.

| Platform | Recommended package | Other supported packages |
| --- | --- | --- |
| Debian/Ubuntu | `schedplus` (Standard) | `schedplus-lite`, `schedplus-cli` |
| Linux portable | Standard AppImage | — |
| Windows | Standard installer | Standard, Lite, Full, and CLI portable ZIPs |
| Microsoft Store | Standard (pending Store approval) | — |
| Snap | Standard (pending Snap publication) | — |

### Debian and Ubuntu

Download the correct architecture-specific `.deb` from a release, then install
it locally. The Standard, Lite, and CLI packages conflict with each other, so
install only one at a time.

```bash
sudo apt install ./schedplus_<version>_<architecture>.deb
# or: sudo apt install ./schedplus-lite_<version>_<architecture>.deb
# or: sudo apt install ./schedplus-cli_<version>_<architecture>.deb
```

Launch the desktop package from your application menu, or run `schedplus`,
`schedplus-lite`, or `schedplus-cli` from a terminal. Remove only the package
when needed; do not use a data-cleaning command unless you intend to erase
tasks:

```bash
sudo apt remove schedplus
```

### AppImage

Make the Standard AppImage executable and run it; no installation is required.

```bash
chmod +x SchedPlus-<version>-x86_64.AppImage
./SchedPlus-<version>-x86_64.AppImage
```

If FUSE is unavailable, extract it instead: `./SchedPlus-<version>-x86_64.AppImage
--appimage-extract`, then run `squashfs-root/AppRun`.

### Windows

Run `SchedPlus-Setup-<version>-windows-x86_64.exe` for the recommended Standard
installation. It is per-user, adds a Start Menu entry, and can be removed from
Windows Settings. Portable releases are ZIP files named
`SchedPlus-<Edition>-<version>-windows-x86_64.zip`; extract one anywhere you
can read it, then start its executable. Do not extract or install into the data
directory below.

The Microsoft Store Standard edition is pending approval. Once published, use
the Store listing rather than a separate installer when you want Store-managed
updates. The Snap Standard edition is likewise pending publication; its future
installation command will be `snap install schedplus`.

### Source installation

Source installs remain available for contributors and users who need the Full
edition. Create a virtual environment, activate it, then choose a profile:

```bash
git clone https://github.com/ZFordDev/SchedPlus.git
cd SchedPlus
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux: source .venv/bin/activate
pip install -e .             # Core scheduler, updater, and CLI
pip install -e ".[lite]"      # Core plus the lightweight Tkinter interface
pip install -e ".[standard]"  # Core plus the advanced PyQt interface
pip install -e ".[full]"      # Every supported interface
```

Tkinter itself is supplied by Python or your operating system; the `lite` extra
adds `tkcalendar`. On some Linux distributions, a package such as `python3-tk`
must be installed separately.

## Usage

For a source Full installation, run `schedplus` without an option to open the
interface selector, or launch an interface directly:

```bash
schedplus         # Open the interface selector
schedplus --tk    # Launch the Tkinter interface
schedplus --py    # Launch the PyQt interface
schedplus --version
```

The installed version is always visible in the desktop footer or sidebar and
in the Full-edition selector. Open **Help → About SchedPlus** in a desktop
interface to see the edition, update channel, package format, platform, and
architecture reported by the installed build.

Tasks can also be managed directly from a terminal without launching a UI:

```bash
# Create a task
schedplus add "Buy milk" --date 2026-08-03 --time 14:00

# List tasks, optionally changing their order
schedplus list
schedplus list --sort time --descending

# Edit a task using its full ID or an unambiguous ID prefix
schedplus edit 7c94a2 --text "Buy milk and bread" --time 15:00

# Delete a task
schedplus delete 7c94a2

# Back up or restore tasks and local preferences
schedplus backup SchedPlus-backup.json
schedplus restore SchedPlus-backup.json --yes

# Export or import portable task data
schedplus export SchedPlus-tasks.json
schedplus import SchedPlus-tasks.json

# Inspect updater state (self-updating packaged builds only)
schedplus update status
schedplus update check
schedplus update install
```

All commands use the same validation and SQLite backend as the desktop
interfaces. Validation and database failures are written to stderr, and each
command returns a process-friendly exit status. Run `schedplus --help` or
`schedplus COMMAND --help` for complete options, or `schedplus --version` to
print the installed application version.

Supported packaged builds verify an Ed25519-signed release manifest and the
downloaded artifact's signed SHA-256 digest before presenting an update.
Windows portable builds activate updates atomically and roll back if the new
release fails its startup health check. Debian and AppImage builds open the
verified download for installation with the platform's normal tools. Microsoft
Store MSIX and Snap packages continue to use Store-managed updates, and source
checkouts stay opted out. The standalone Windows installer remains opted out
until public Authenticode signing is configured.

Use **Help → Check for updates** and **Help → Last update result** in PyQt, or
the equivalent **Settings** menu commands in Tkinter. Automatic checks can be
enabled or disabled in Settings. Update failures are reported without blocking
application startup.

## Your data, upgrades, and removal

Packages never write task data into their installation directory. The SQLite
database and `schedplus.log` use these per-user locations:

| Package environment | Data location |
| --- | --- |
| Windows installer, portable ZIP, and MSIX | `%APPDATA%\ZFordDev\SchedPlus\tasks.db` |
| Normal Linux, Debian, and AppImage | `~/.local/share/ZFordDev/SchedPlus/tasks.db` |
| Strict Snap | `$SNAP_USER_COMMON/SchedPlus/tasks.db` |

Upgrades retain this data. Removing an installer, `.deb`, Snap, or AppImage
does not delete it. Back up `tasks.db` while SchedPlus is closed before a major
upgrade; installations from 0.7.3 and earlier automatically move the old
in-application database to the appropriate user-data location when possible.

SchedPlus records its SQLite schema version and applies required migrations in
order inside a transaction. Before changing an existing schema, it creates a
timestamped `tasks_pre_migration_v<old>_to_v<new>_*.db` backup beside
`tasks.db`. A failed migration rolls back, and an older SchedPlus build refuses
to open a database written with a newer schema version without modifying it.

The **Data** menu in either desktop interface can create and restore a complete
local backup or export and import tasks. Backup and task-export files are
versioned JSON and never leave your computer. Restore validates the entire file
before replacing tasks and automatically saves the current data under the
application data directory first. Import never overwrites an existing ID:
identical records are counted as duplicates, records with the same ID but
different values are counted as conflicts, and both are skipped.

## System requirements

- Windows 10 or later, or a modern Linux distribution
- A desktop environment for graphical modes
- Python 3.10 or later only for source installations
- Tkinter (and, on some Linux systems, `python3-tk`) only for the Lite source profile

_macOS is not currently supported._

## Build from source

You will need Python 3.10 or later, pip, and Git. Tkinter may need to be installed through your operating system's package manager.

```bash
git clone https://github.com/ZFordDev/SchedPlus.git
cd SchedPlus
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

The development profile includes both desktop interfaces along with the test,
formatting, and linting tools.

## Project status and roadmap

SchedPlus is actively developed and open to contributions. Current work is focused on strengthening the desktop experience and expanding SchedPlus beyond task management into a complete scheduling platform.

Planned areas include:

- Reminders and notifications
- Optional syncing across devices
- Accounts for sync and connected features
- Improved task management workflows
- Additional platform packages and Store publication
- Continued development of the PyQt interface

Development priorities evolve with user feedback. Follow the live project trackers for current plans:

- [Open issues and planned improvements](https://github.com/ZFordDev/SchedPlus/issues)
- [Latest releases and release notes](https://github.com/ZFordDev/SchedPlus/releases)
- [Contributing guide](CONTRIBUTING.md)

## Known limitations

- Advanced calendar features such as recurring events and categories are not yet available.
- Snap and Microsoft Store publication are pending approval.
- Syncing, accounts, and reminders are planned features and are not yet available.
- macOS is not currently supported.

## Support and contributing

Bug reports, feature ideas, documentation improvements, and code contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change, and use the [issue tracker](https://github.com/ZFordDev/SchedPlus/issues) for bugs and suggestions.

Security vulnerabilities should be reported using the process in [SECURITY.md](SECURITY.md), not through a public issue.

If SchedPlus is useful to you, starring the repository or sharing the project also helps.

## License

SchedPlus uses a clear licensing boundary:

- The complete native desktop application is licensed under
  [GPL-3.0-only](LICENSE). This includes the distributed application that uses
  GPL-licensed PyQt6.
- The reusable scheduler, validation, task model, and storage modules under
  `src/logic` are separately available under the
  [Apache License 2.0](LICENSES/Apache-2.0.txt).
- Third-party dependencies remain governed by their respective licenses.

Releases through version 0.7.3 used a blanket MIT license. The final source
available entirely under those terms is preserved in the
[`release-0.7.3`](https://github.com/ZFordDev/SchedPlus/tree/release-0.7.3)
tag, and the historical [MIT license text](LICENSES/MIT.txt) remains included
for attribution and reference. See [NOTICE](NOTICE) for the complete licensing
and transition notice.

## About

SchedPlus is part of the ZFordDev ecosystem, a collection of focused tools built for clarity, practical use, and long-term maintainability. It is built and maintained by [ZFordDev](https://github.com/ZFordDev).
