<div align="center">

# SchedPlus

### A lightweight, local‑first desktop scheduler built in Python.  

[Documentation](https://docs.zford.dev/zforddev/schedplus/) · [Downloads](https://github.com/ZFordDev/SchedPlus/releases) · [Report a bug](https://github.com/ZFordDev/SchedPlus/issues/new/choose)

![Status](https://img.shields.io/badge/Status-ACTIVE-4CAF50?style=flat-square)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-0078D4?style=flat-square)](#installation)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

</div>

## Why This Exists

Most scheduling tools try to do everything — calendars, reminders, syncing, accounts, cloud dashboards — and end up feeling heavy or overly complex.

SchedPlus is intentionally the opposite:

- **simple**
- **local‑first**
- **lightweight**
- **predictable**
- **no accounts**
- **no cloud**
- **no clutter**

It focuses on one job: helping you plan your day without getting in your way.

## Overview

SchedPlus is a clean, predictable desktop scheduler built for people who want structure without noise.

It emphasizes:

- fast startup  
- a minimal interface  
- local‑only task storage  
- a small, readable Python codebase  
- an offline‑first workflow  

SchedPlus currently ships with a stable Tkinter UI, while a full PyQt migration is underway to deliver a more modern, cross‑platform experience.

## Features

- Local task creation and management  
- SQLite-based local storage
- Offline‑first workflow  
- Tkinter UI (stable)  
- PyQt UI (in development)  
- Clean logic/storage separation  
- Beginner‑friendly codebase  

## Requirements
To run or develop it, you’ll need:

> Python 3.10+  
> pip
> Tkinter  
> PyQt6 

**Supported environments:**

> Windows 10+  
> Linux (Ubuntu 24.04+)

## Quick Start

```bash
git clone https://github.com/ZFordDev/schedplus.git
cd schedplus

# Create and activate a virtualenv (recommended)
python -m venv .venv
source .venv/bin/activate

# Install in editable mode for local development
pip install -e .

# Run (choose one):
# - console script installed by pip
schedplus
# - run as a module
python -m schedplus
# - run from source without installing (development)
cd src
python -m main
```

> *Recommended: use a `.venv`.*

## Installation

SchedPlus binaries will be available once the packaging pipeline is complete.  
Until then, install from source:

```bash
pip install e.
```

## Usage

Basic usage:

```bash
schedplus
```

The UI will open and allow you to create, edit, and save tasks locally.

## Project Structure

SchedPlus uses a simple, predictable layout designed to keep UI, logic, and data clearly separated.

```text
schedplus/
├── src/
│   └── schedplus/
│       ├── assets/        # Icons and UI assets
│       ├── data/          # Local task storage
│       ├── logic/         # Core scheduling logic
│       ├── startup/       # Application startup flow
│       ├── ui/            # Tkinter + PyQt interfaces
│       └── __main__.py    # Application entry point
│
└── packaging/             # Future packaging targets
    ├── snap/
    ├── deb/
    └── windows/
```

## Roadmap
 
- [ ] Cross‑platform packaging  
- [ ] Windows installer  
- [ ] Improved task management  
- [ ] UI backend experimentation  
- [ ] Multi‑platform releases  

## Screenshots

<p align="center">
  <img src="assets/screenshots/schedplus-tkinter.png" width="45%" />
  <img src="assets/screenshots/schedplus-pyqt.png" width="45%" />
</p>

## Known Issues

- PyQt UI is incomplete  
- Packaging is experimental  
- macOS support not yet available  

## Support

You can support SchedPlus by:

- Leaving a ⭐ on GitHub  
- Reporting bugs  
- Suggesting new features  
- Improving documentation  
- Contributing code  

## Contributing

Contributions, bug reports, feature requests, and feedback are welcome.

See `CONTRIBUTING.md` for project‑specific guidelines.  
For ecosystem‑wide expectations, see **[STANDARDS.md](https://github.com/ZFordDev/ZFordDev/blob/main/STANDARDS.md)**.

## Security

See `SECURITY.md` for vulnerability reporting guidelines.  
If no security policy is present, please report issues responsibly via GitHub Issues.

## License

Released under the MIT License.  
See `LICENSE` for details.

## About ZFordDev

This project is part of the ZFordDev ecosystem — a collection of lightweight, practical tools built with clarity, simplicity, and long‑term maintainability in mind.

For ecosystem‑wide standards, see **STANDARDS.md**.
