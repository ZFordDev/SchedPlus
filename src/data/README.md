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
    updatedAt TEXT NOT NULL,
    completed TEXT NOT NULL DEFAULT '',
    completedAt TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    priority TEXT NOT NULL DEFAULT '',
    duration TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT '',
    recurrence TEXT NOT NULL DEFAULT '',
    recurrenceEnd TEXT NOT NULL DEFAULT '',
    reminder TEXT NOT NULL DEFAULT ''
);
```

This is the current schema after migrations 1 through 6. UUIDs provide stable
task identifiers, ISO timestamps support sorting and portable transfer, and
the task fields remain UI-independent.

## Schema migrations

The current schema version is stored in SQLite's `PRAGMA user_version`.
Released migration functions live in the ordered `MIGRATIONS` tuple in
`logic/storage/migrations.py`. Never edit or reorder a released migration; add
one new callable at the end so every database follows the same version path.

Initialization performs an integrity check before migration. When an existing
database is behind the application schema, SchedPlus creates a consistent
`tasks_pre_migration_v<old>_to_v<new>_<timestamp>.db` backup in the data
directory, then runs every missing migration and version update in one
transaction. Any failure rolls the transaction back and leaves both the
original database and backup available.

Databases from v0.7.3 and v0.8.0 have the version-zero form of the `entries`
table and are adopted by migration 1 without changing task rows. A build will
not downgrade a newer database: when `user_version` is greater than the version
it supports, it exits the storage operation without modifying or backing up the
database and asks the user to install a newer SchedPlus release.

Corruption handling is separate from schema migration. A failed integrity check
still preserves the damaged file as `tasks_corrupted_<timestamp>.db` and creates
a clean database at the current schema version.

## User backups and task exports

User-created backups are UTF-8 JSON objects identified by
`"format": "schedplus-backup"` and `"format_version": 1`. They contain the
application version, creation time, complete task records, automatic-update
preference, and portable PyQt UI preferences when available. Restore validates
the format, version, preferences, every field, and every task before making any
change. It then creates `backups/SchedPlus-before-restore-<timestamp>.json`
under the user data directory before replacing tasks through the current
database schema.

Portable task exports use `"format": "schedplus-task-export"`, version 1, and
contain task records but no preferences. Import is additive: a new ID is
inserted, an identical existing ID is skipped as a duplicate, and an existing
ID with different values is skipped as a conflict. Equal task content under a
different ID remains a separate task. These operations only access local files;
they do not upload or transmit data.
