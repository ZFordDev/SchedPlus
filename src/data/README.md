# Storage Overview  
SchedPlus uses a **local‑first**, **user‑owned** storage model.  
Older versions stored tasks in a JSON file, while newer versions use a SQLite database. Both formats share the same conceptual schema, ensuring compatibility across all UIs (Tkinter, PyQt, RAW CLI, and future Pro interfaces).

The storage folder may contain:

- legacy `tasks.json` files  
- the new `tasks.db` SQLite database  
- future extension tables linked by UUID  

After the first successful migration, the JSON file is usually safe to delete — but backing it up is recommended.

---

# Core Schema (V1 – Stable, Minimal, Future‑Proof)

```
{
  "version": 1,
  "tasks": [
    {
      "id": "UUID",
      "date": "Date input",
      "time": "Time input",
      "text": "Text input",
      "createdAt": "unique at time of creation",
      "updatedAt": "updated if entry changed"
    }
  ]
}
```

The SQLite version mirrors this structure:

```
entries (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    text TEXT NOT NULL,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL
)
```

This schema is intentionally minimal:

- **UUID** → universal linking key  
- **ISO timestamps** → perfect for sorting, syncing, merging  
- **date/time/text** → UI‑agnostic, human‑readable  
- **no foreign keys** → safe for all UIs, including legacy ones  

This is the **SchedPlus Core**, and it will not change.

---

# Why We Don’t Modify the Core Table  
SchedPlus is designed as a **platform**, not a single app.  
Multiple UIs (Tkinter, PyQt, RAW, Dev, SysAdmin, Admin, Pro) all rely on the same core logic.

Changing the core schema would break:

- older UIs  
- third‑party tools  
- CLI scripts  
- user data portability  

Instead, **all future features attach to the UUID** using additional tables.

This keeps SchedPlus:

- backward compatible  
- forward expandable  
- UI‑agnostic  
- safe for open‑source users  
- powerful for Pro users  

---

# The Future: Extension Tables (SchedPlus‑Pro, Dev, SysAdmin, Admin)

Instead of modifying `entries`, new features will use **linked tables**:

- **entry_meta** -> priority, status, color  
- **entry_links** -> file paths, git commits, servers, calendar events  
- **entry_tags** -> tagging system  
- **entry_comments** -> threaded notes  
- **entry_sync** -> cloud/team sync metadata  

All linked by:

```
entry_id TEXT REFERENCES entries(id)
```

---
