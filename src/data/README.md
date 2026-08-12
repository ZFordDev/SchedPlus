# Storage Overview

SchedPlus uses SQLite as its sole persistence backend. Task data is stored in the
platform-specific, user-owned data directory rather than inside this package.

## Data locations

SchedPlus never creates task data inside its installation directory. The SQLite
database is stored at the following user-owned locations:

- Standard Linux and AppImage: `~/.local/share/ZFordDev/SchedPlus/tasks.db`
- Strict Snap: `$SNAP_USER_COMMON/SchedPlus/tasks.db` (shared across revisions)
- Windows: `%APPDATA%\\ZFordDev\\SchedPlus\\tasks.db`
- macOS: `~/Library/Application Support/ZFordDev/SchedPlus/tasks.db`

If `SNAP_USER_COMMON` is absent or empty, SchedPlus safely falls back to the
standard Linux location. The one-time migration from the pre-0.8.0 package-local
database is performed only when no destination database already exists.

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
