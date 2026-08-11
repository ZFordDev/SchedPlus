# Storage Overview

SchedPlus uses SQLite as its sole persistence backend. Task data is stored in the
platform-specific, user-owned data directory rather than inside this package.

## Core Schema

```sql
CREATE TABLE entries (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    text TEXT NOT NULL,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL
);
```

The schema is intentionally minimal. UUIDs provide stable linking keys, ISO
timestamps support sorting and synchronization, and the task fields remain
UI-independent. Future features can use additional tables linked through the
entry ID without changing the core table.
