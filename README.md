[![Website](https://img.shields.io/badge/Website-zford.dev-000000?style=flat-square)](https://zford.dev)
[![Ko‑Fi](https://img.shields.io/badge/Support-KoFi-FF5E5B?style=flat-square)](https://ko-fi.com/zforddev)

# **SchedPlus**

_A small Python app that teaches you how real software evolves._

Build a simple scheduler.  
Then improve it.  
Then refactor it.  
Then migrate the UI.  
Then package it.  
Then ship it.

SchedPlus isn’t a one-off tutorial — it’s a **step-by-step evolution of a real project**.

You can start at the first commit and follow every decision, every mistake, and every improvement along the way.

---

## **Why SchedPlus Exists**

Most tutorials show you how to build something once.

SchedPlus shows you how software actually grows.

You’ll go from a basic Tkinter script to a structured, cross-platform desktop app — learning how to:

- change code without breaking it
- separate UI from logic
- migrate frameworks (Tkinter → PyQt)
- package apps for real users
- ship a complete release

This is the part most tutorials skip.

**Version history:**  
https://github.com/zforddev/schedplus/commits/main  
_Recommended: start at the earliest commit and work forward._

---

## **What You’ll Learn**

SchedPlus is a step‑by‑step journey through:

- Python basics
- Tkinter GUI programming
- PyQt GUI programming (later)
- JSON storage
- JSON schema design
- basic persistence layer
- safe file handling
- clean project structure
- refactoring techniques
- cross‑platform packaging
  - Snap (Linux)
  - .deb (Debian/Ubuntu)
  - Windows .exe
- versioning and release workflow

**Full learning documents:**  
https://docs.zford.dev/docs/schedplus/

---

## **Project Roadmap (Learning Journey)**

SchedPlus will evolve through these stages:

1. **v0.1 — Basic Tkinter UI**
2. **v0.2 — Save & Load (JSON)**
   - Added tasks.json persistence
   - Defined official task schema
   - Implemented save/load with error handling
3. **v0.3 — Logic Layer Separation**
4. **v0.4 — Prepare for PyQt Migration**
5. **v0.5 — PyQt UI Added**
6. **v0.6 — UI Switching (Tkinter ↔ PyQt)**
7. **v0.7 — Snap Packaging**
8. **v0.8 — .deb Packaging**
9. **v0.9 — Windows Packaging**
10. **v1.0 — Multi‑Platform Release**

Each version teaches something new.

---

## **Project Structure (v0.1)**

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

This structure is designed for growth.  
UI and logic are separate so we can migrate toolkits without rewriting the app.

---

## **Running SchedPlus (v0.1)**

```
python3 src/main.py
```

Later versions will include:

- Snap installation
- .deb installation
- Windows installer

---

## **Contributing**

SchedPlus is designed to be forked, modified, and experimented with.  
If you’re learning Python, GUI programming, or packaging — this project is for you.

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

---

## **License**

MIT License — free to use, modify, and learn from.

---

## **Explore More**

🌐 **zford.dev** — https://zford.dev  
🎮 **Itch.io** — https://zforddev.itch.io  
❤️ **Ko‑Fi** — https://ko-fi.com/zforddev
