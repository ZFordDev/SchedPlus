<!-- ========================================================= -->
<!-- Standards Approval Badge -->
<!-- ========================================================= -->

<table align="right">
  <tr>
    <td>
      <img src="https://raw.githubusercontent.com/ZFordDev/ZFordDev/main/assets/standards-approved.svg" width="80" alt="ZFordDev Standards Approved Badge">
    </td>
  </tr>
</table>

<!-- ========================================================= -->
<!-- Required Badges -->
<!-- ========================================================= -->

[![Docs](https://img.shields.io/badge/DocsHub-docs.zford.dev-4F46E5?style=flat-square)](https://docs.zford.dev)
![Status](https://img.shields.io/badge/Status-ACTIVE-4CAF50?style=flat-square)
![Platforms](https://img.shields.io/badge/Platforms-Windows%20%7C%20Linux-blue?style=flat-square)

<!-- ========================================================= -->
<!-- Optional Badges -->
<!-- ========================================================= -->

<!-- [![itch.io](https://img.shields.io/badge/itch.io-SchedPlus-FA5C5C?style=flat-square)](https://zforddev.itch.io/schedplus) -->
<!-- ![Downloads](https://img.shields.io/github/downloads/ZFordDev/SchedPlus/total?style=flat-square) -->
![Python](https://img.shields.io/badge/Built_with-Python-blue?style=flat-square)

# SchedPlus

> A lightweight, local‑first desktop scheduler built in Python.  
> **Status:** Alpha • Actively Maintained • Accepting Contributions

---

## Why This Exists

Most scheduling tools try to do everything — calendars, reminders, syncing, accounts, cloud dashboards — and end up feeling heavy, slow, or overly complex.

SchedPlus was built to be the opposite:

- **simple**
- **local‑first**
- **lightweight**
- **predictable**
- **no accounts**
- **no cloud**
- **no unnecessary features**

It focuses on one job: helping you plan your day without getting in your way.

SchedPlus is also a great **learning reference**, showing how a real desktop app evolves over time — from a quick Tkinter prototype to a structured Python application and eventually a full PyQt desktop experience.

---

## Overview

SchedPlus is a simple, predictable desktop scheduler built for people who want structure without the noise.

It focuses on:

- fast startup  
- a clean, minimal interface  
- local‑only task storage  
- a small, readable Python codebase  
- an offline‑first workflow  

It’s intentionally lightweight — ideal for daily planning, learning Python UI development, or experimenting with how real desktop apps evolve over time.

SchedPlus currently ships with a stable Tkinter UI, while a full PyQt migration is actively underway to bring a more modern, cross‑platform experience.

---

## Features

* Local task creation and management  
* JSON‑based save/load  
* Offline‑first workflow  
* Tkinter UI (stable)  
* PyQt UI (in development)  
* Clean logic/storage separation  
* Beginner‑friendly codebase  

---

## Requirements

SchedPlus is currently a source‑only project.  
To run or develop it, you’ll need:

> Python 3.14+  
> pip (latest)  
> Tkinter (included with most Python installs)  
> PyQt6 (optional, for the new UI)  

**Supported environments:**

> Windows 10+  
> Linux (Ubuntu 22.04+)  

---

## Quick Start

```bash
git clone https://github.com/ZFordDev/schedplus.git
cd schedplus

pip install -r requirements.txt

python3 src/main.py
```

> *Recommended: use a `.venv`.*

---

## Installation

SchedPlus currently has no build pipeline yet — please wait for the beta release.

---

## Usage

Basic usage:

```bash
python3 src/main.py
```

The UI will open and allow you to create, edit, and save tasks locally.

---

## Project Structure

SchedPlus uses a simple, predictable layout designed to keep UI, logic, and data clearly separated.

```text
schedplus/
├── src/
│   ├── assets/          # Icons and UI assets
│   ├── data/            # Local task storage
│   ├── logic/           # Core scheduling logic
│   ├── startup/         # NEW — startup
│   ├── ui/              # Tkinter + PyQt interfaces
│   └── main.py          # Application entry point
│
└── packaging/           # Future packaging targets
    ├── snap/
    ├── deb/
    └── windows/
```

---

## Roadmap

* [ ] Full PyQt migration  
* [ ] Cross‑platform packaging  
* [ ] Windows installer  
* [ ] Improved task management  
* [ ] UI backend experimentation  
* [ ] Multi‑platform releases  

---

## Screenshots

<p align="center">
  <img src="assets/screenshots/schedplus-tkinter.png" width="45%" />
  <img src="assets/screenshots/schedplus-pyqt.png" width="45%" />
</p>

---

## Known Issues

* PyQt UI is incomplete  
* Packaging is experimental  
* macOS support not yet available  

---

## Related Projects

- **MathPlus** — a lightweight desktop calculator  
  [https://github.com/ZFordDev/MathPlus](https://github.com/ZFordDev/MathPlus)  

---

## Support

You can support SchedPlus by:

* Leaving a ⭐ on GitHub  
* Reporting bugs  
* Suggesting new features  
* Improving documentation  
* Contributing code  

---

## Contributing

Contributions, bug reports, feature requests, and feedback are welcome.

See `CONTRIBUTING.md` for project‑specific guidelines.  
For ecosystem‑wide expectations, see [STANDARDS.md](https://github.com/ZFordDev/ZFordDev/blob/main/STANDARDS.md).

---

## Security

See `SECURITY.md` for vulnerability reporting guidelines.  
If no security policy is present, please report issues responsibly via GitHub Issues.

---

## License

Released under the MIT License.  
See `LICENSE` for details.

---

## About ZFordDev

This project is part of the ZFordDev ecosystem — a collection of lightweight, practical tools built with clarity, simplicity, and long‑term maintainability in mind.

For ecosystem‑wide standards, see [STANDARDS.md](https://github.com/ZFordDev/ZFordDev/blob/main/STANDARDS.md).

---