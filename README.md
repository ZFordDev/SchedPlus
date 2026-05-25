# **SchedPlus — A Clean, Evolving Desktop Scheduler**

<p align="center">
  <img src="https://img.shields.io/github/v/release/zforddev/schedplus?style=for-the-badge&color=78C2AD" alt="Version">
  <img src="https://img.shields.io/github/license/zforddev/schedplus?style=for-the-badge&color=blue" alt="License">
  <img src="https://img.shields.io/github/stars/zforddev/schedplus?style=for-the-badge&color=FFD700" alt="Stars">
</p>

SchedPlus is a lightweight desktop scheduler built in the open — evolving from a small Tkinter prototype into a structured cross-platform desktop application.

The project doubles as both a real productivity tool and a transparent learning journey, showing how software evolves version by version.

It’s intentionally simple:
not a calendar replacement, not a productivity suite — just a clean, predictable scheduler designed to stay lightweight and easy to understand.

---

## 💡 Why SchedPlus Exists

Most tutorials teach you how to build a project once.

SchedPlus focuses on something different:
how software evolves over time.

The project documents the transition from:
- quick prototype
- to structured application
- to multi-platform desktop software

…without constantly rewriting everything from scratch.

It’s designed to be approachable for beginners while still demonstrating real project structure, refactoring, and long-term growth.

---

## ✨ Current Features

- Create and manage tasks locally
- Save/load schedules using JSON
- Lightweight desktop interface
- Offline-first workflow
- Tkinter UI with PyQt migration in progress
- Structured logic and storage separation

---

## ✨ Philosophy

SchedPlus follows a few core principles:

- **Clarity over complexity** — simple UI, simple logic, simple storage
- **Local-first** — your tasks stay on your machine
- **Transparent evolution** — every version teaches something
- **Refactor-friendly** — clean structure, no hidden magic
- **Cross-platform mindset** — built to run everywhere

---

## 🛠 Current State

| Version | Status | Focus |
|---|---|---|
| **v0.1** | Stable | Basic Tkinter interface |
| **v0.2** | Stable | JSON save/load |
| **v0.3** | Stable | Logic separation |
| **v0.4** | Stable | PyQt preparation |
| **v0.5** | Active Development | Full PyQt integration |

---

## 📦 Running SchedPlus

```bash
python3 src/main.py
````

Future releases will include:

* Snap packages
* `.deb` packages
* Windows installers

---

## 🧭 Roadmap

Current direction includes:

* Full PyQt migration
* Cross-platform packaging
* Windows installer support
* Improved task management
* UI backend experimentation
* Multi-platform releases

Each version of SchedPlus is intended to teach something new about real software development.

---

## 🗂 Project Structure

```text
schedplus/
│
├── src/
│   ├── main.py
│   ├── logic/
│   │   ├── scheduler.py
│   │   └── storage.py
│   │
│   ├── ui/
│   │   ├── tkinter_ui.py
│   │   └── pyqt_ui.py
│   │
│   └── tasks.json
│
├── packaging/
│   ├── snap/
│   ├── deb/
│   └── windows/
│
└── README.md
```

---

## 📖 Documentation & Links

### Learning Documentation

[https://docs.zford.dev/docs/schedplus/](https://docs.zford.dev/docs/schedplus/)

### Commit History

[https://github.com/zforddev/schedplus/commits/main](https://github.com/zforddev/schedplus/commits/main)

---

## 👥 Contributing

SchedPlus welcomes contributors of all skill levels.

Whether you're learning Python, experimenting with desktop UI development, or helping shape the PyQt migration, pull requests are always appreciated.

### Good areas to contribute

* PyQt UI improvements
* Packaging support
* UI/UX polish
* Task management features
* Validation and error handling
* Cross-platform testing

Issues marked with:

* `good first issue`
* `help wanted`
* `UI/UX`

…are especially beginner-friendly.

---

## ❤️ Contributors

SchedPlus continues to evolve thanks to community contributions.

### Special Thanks

**@shivmodi**

* improved task architecture using Python dataclasses
* added JSON-safe timestamps and load/save integration
* improved Tkinter task loading behavior

**@peetsboy**

* contributed early task system improvements
* helped shape the foundation of the task model

**@Zeaforx**

* added shortcut creation support via `ui/shortcuts.py`
* improved groundwork for desktop integration

**@preetisingh172003**

* contributed date and time validation improvements for the Tkinter UI

Thank you to everyone helping SchedPlus grow in the open.

---

## ❤️ Support the Project

If SchedPlus helps you learn or stay organized, consider supporting the project:

* ⭐ Star the repository
* ☕ Ko-Fi: [https://ko-fi.com/zforddev](https://ko-fi.com/zforddev)

---

## 📄 License

Released under the MIT License.

See `LICENSE` for details.
