# Task JSON Schema

SchedPlus stores scheduled tasks in JSON using a simple versioned schema.

## Task Object Structure

Each task is represented as an object with the following fields:

- `id` — unique task identifier (string, `uuid4` recommended)
- `date` — ISO date in `YYYY-MM-DD` format
- `time` — 24-hour time in `HH:MM` format
- `text` — task description
- `createdAt` — creation timestamp in epoch milliseconds
- `updatedAt` — last update timestamp in epoch milliseconds

## Full File Layout

The top-level file contains a `version` field and a `tasks` array.

```json
{
  "version": 1,
  "tasks": [
    {
      "id": "uuid",
      "date": "2026-05-04",
      "time": "14:30",
      "text": "Example task",
      "createdAt": 1714820000000,
      "updatedAt": 1714820000000
    }
  ]
}
```

## Notes

- The `version` field supports future migrations.
- The schema uses ISO date/time formats for clarity.
- The file is intentionally simple and beginner-friendly.
