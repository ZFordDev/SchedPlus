# **SchedPlus — A Clean, Evolving Desktop Scheduler**

<p align="center">
  <img src="https://img.shields.io/github/v/release/zforddev/schedplus?style=for-the-badge&color=78C2AD" alt="Version">
  <img src="https://img.shields.io/github/license/zforddev/schedplus?style=for-the-badge&color=blue" alt="License">
  <img src="https://img.shields.io/github/stars/zforddev/schedplus?style=for-the-badge&color=FFD700" alt="Stars">
</p>

SchedPlus is a simple, modern task scheduler built in the open — evolving from a tiny Tkinter script into a structured, cross‑platform desktop app.  
It’s both a **real tool** and a **transparent learning journey**, showing how software grows version by version.

---

## 💡 Why SchedPlus Exists

Most tutorials show you how to build something once.

SchedPlus shows you how real software evolves:

- from a basic UI  
- to a structured logic layer  
- to a PyQt migration  
- to a packaged, cross‑platform application  

It’s a practical, real‑world example of how to grow a project without throwing everything away each time.

SchedPlus is intentionally simple — not a calendar replacement, not a productivity suite — just a clean, predictable scheduler that teaches you how real apps are built.

---

## ✨ Philosophy

SchedPlus follows a few core principles:

- **Clarity over complexity** — simple UI, simple logic, simple storage  
- **Local‑first** — your tasks stay on your machine  
- **Transparent evolution** — every version teaches something  
- **Refactor‑friendly** — clean structure, no hidden magic  
- **Cross‑platform mindset** — built to run everywhere  

---

## 🛠 Current State

| Version | Status | Focus |
|--------|--------|--------|
| **v0.1** | Stable | Basic Tkinter UI |
| **v0.2** | Stable | JSON save/load |
| **v0.3** | Stable | Logic layer separation |
| **v0.4** | In Dev | PyQt preparation (UI selector, skeleton UI) |
| **v0.5+** | Planned | Full PyQt UI, packaging, multi‑platform release |

---

## 📦 Installation

For now:

```
python3 src/main.py
```

Future versions will include:

- Snap package  
- .deb package  
- Windows installer  

---

## 📖 Documentation & Links

**Learning Docs:**  
[https://docs.zford.dev/docs/schedplus/](https://docs.zford.dev/docs/schedplus/)

**Version History:**  
[https://github.com/zforddev/schedplus/commits/main](https://github.com/zforddev/schedplus/commits/main)

---

## 🧭 Project Roadmap

SchedPlus evolves through these stages:

1. **v0.1 — Basic Tkinter UI**  
2. **v0.2 — Save & Load (JSON)**  
3. **v0.3 — Logic Layer Separation**  
4. **v0.4 — Prepare for PyQt Migration**  
   - UI selector (Tkinter ↔ PyQt)  
   - PyQt UI skeleton  
   - Shared logic cleanup (if needed)  
5. **v0.5 — PyQt UI Added**  
6. **v0.6 — UI Switching (Tkinter ↔ PyQt)**  
7. **v0.7 — Snap Packaging**  
8. **v0.8 — .deb Packaging**  
9. **v0.9 — Windows Packaging**  
10. **v1.0 — Multi‑Platform Release**

Each version teaches something new.

---

## 🗂 Project Structure

```
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
│   │   └── pyqt_ui.py   # added later
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

## 👥 Contributing

SchedPlus welcomes contributors of all skill levels.  
Whether you're learning Python or helping shape the PyQt UI, PRs are always appreciated.

---

## Recent Improvements: Task Class & JSON Integration

This PR (#12) adds the following enhancements:

- `Task` class is now a **dataclass** with automatic UUID and ISO timestamps
- `createdAt` and `updatedAt` fields are **JSON-safe ISO strings**
- `storage.py` updated:
  - `save_tasks()` converts Task objects → dict → JSON
  - `load_tasks()` converts JSON → dict → Task objects
- Tkinter UI (`tkinter_ui.py`) updated:
  - Populate listbox with **existing tasks from JSON** at startup
  - Append **only the newly added task** to listbox
  - Save tasks immediately to JSON after adding
- `main.py` now **loads tasks from JSON before launching UI**

## ❤️ Support the Project

If SchedPlus helps you learn or stay organized, consider supporting the work:

- ⭐ **Star the repo** to help others discover it  
- ☕ **Ko‑Fi**: [https://ko-fi.com/zforddev](https://ko-fi.com/zforddev)  

---

## 👤 Credits

Created and maintained by **ZFordDev**.  

**Contrabiutors:**  
- @shivmodi - #12
- @peetsboy - #11
- @Zeaforx - #5

---
