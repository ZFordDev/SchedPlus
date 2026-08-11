<div align="center">

# SchedPlus

### A modern, local-first scheduler for Windows and Linux

[Documentation](https://docs.zford.dev/zforddev/schedplus/) · [Downloads](https://github.com/ZFordDev/SchedPlus/releases) · [Report a bug](https://github.com/ZFordDev/SchedPlus/issues/new/choose)

[![Status](https://img.shields.io/badge/status-active-4CAF50?style=flat-square)](https://github.com/ZFordDev/SchedPlus)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-0078D4?style=flat-square)](#installation)
[![GitHub downloads](https://img.shields.io/github/downloads/ZFordDev/SchedPlus/total?style=flat-square)](https://github.com/ZFordDev/SchedPlus/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

</div>

SchedPlus gives you a focused place to organise tasks and plan your time without unnecessary friction. It is local-first, offline-friendly, and growing into a broader scheduling platform with calendars, reminders, syncing, and accounts on the roadmap.

<p align="center">
  <img src="assets/screenshots/schedplus-tkinter.png" width="48%" alt="SchedPlus Tkinter interface" />
  <img src="assets/screenshots/schedplus-pyqt.png" width="48%" alt="SchedPlus PyQt interface" />
</p>

## Features

- **Local task management** for creating, viewing, updating, and deleting scheduled tasks
- **SQLite persistence** stored in the platform-appropriate user data directory
- **Offline-friendly workflow** with task data kept on your computer
- **Multiple interfaces** including lightweight Tkinter, the advanced PyQt task workspace, and a raw CLI
- **Cross-platform foundation** targeting Windows and Linux
- **Shared scheduling core** that keeps persistence and interface code separated

## Installation

Packaged releases are planned. Until installers are available, install SchedPlus from source:

```bash
git clone https://github.com/ZFordDev/SchedPlus.git
cd SchedPlus

python -m venv .venv
source .venv/bin/activate
pip install -e .

schedplus
```

On Windows, activate the virtual environment with `.venv\Scripts\activate` before running the remaining commands.

## Usage

Run `schedplus` without an option to open the interface selector, or launch an interface directly:

```bash
schedplus         # Open the interface selector
schedplus --tk    # Launch the Tkinter interface
schedplus --py    # Launch the PyQt interface
schedplus --raw   # Use the raw command-line interface
```

Run `schedplus --raw help` for the commands available in raw mode.

## System requirements

- Python 3.10 or later
- Windows 10 or later, or a modern Linux distribution
- Tkinter for the Tkinter interface
- A desktop environment for graphical modes

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

## Project status and roadmap

SchedPlus is actively developed and open to contributions. Current work is focused on strengthening the desktop experience and expanding SchedPlus beyond task management into a complete scheduling platform.

Planned areas include:

- Calendars and calendar-based planning
- Reminders and notifications
- Optional syncing across devices
- Accounts for sync and connected features
- Improved task management workflows
- Cross-platform installers and packaged releases
- Continued development of the PyQt interface

Development priorities evolve with user feedback. Follow the live project trackers for current plans:

- [Open issues and planned improvements](https://github.com/ZFordDev/SchedPlus/issues)
- [Latest releases and release notes](https://github.com/ZFordDev/SchedPlus/releases)
- [Contributing guide](CONTRIBUTING.md)

## Known limitations

- The PyQt task workspace is functional, while its native calendar views remain under development.
- Packaged installers are not yet available.
- Syncing, accounts, calendars, and reminders are planned features and are not yet available.
- macOS is not currently supported.

## Support and contributing

Bug reports, feature ideas, documentation improvements, and code contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change, and use the [issue tracker](https://github.com/ZFordDev/SchedPlus/issues) for bugs and suggestions.

Security vulnerabilities should be reported using the process in [SECURITY.md](SECURITY.md), not through a public issue.

If SchedPlus is useful to you, starring the repository or sharing the project also helps.

## License

SchedPlus is free and open-source software released under the [MIT License](LICENSE).

## About

SchedPlus is part of the ZFordDev ecosystem, a collection of focused tools built for clarity, practical use, and long-term maintainability. It is built and maintained by [ZFordDev](https://github.com/ZFordDev).
