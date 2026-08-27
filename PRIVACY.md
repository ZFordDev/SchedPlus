# SchedPlus Privacy Policy

**Effective date:** v0.9.0 (August 2026)

## Local-first guarantee

SchedPlus is a local-first desktop application. In the current 0.9.x releases,
all task data, backups, and user preferences are stored on your device and are
not uploaded or synchronized. Supported packages may use the network for
application updates as described below.

## What data SchedPlus stores

| Data | Where it is stored | Purpose |
| --- | --- | --- |
| Tasks (text, dates, notes, priority, duration, category, recurrence, reminder) | Local SQLite database | Core task management |
| Completed-task history | Same local database | Undo and task recovery |
| UI preferences (sort, filter, date/time format, week numbers) | Local QSettings / portable JSON | Personalization |
| Update state (last check, target version) | Local file in user data directory | Update management |

## What current releases do not do

- **No account is required.** Current releases have no registration, login, or
  online user profile, and core task management works offline.
- **No network transmission of task data.** Tasks never leave your device.
- **No analytics or telemetry.** SchedPlus does not collect usage data.
- **No ads or tracking.** There are no advertising identifiers or trackers.
- **No cloud sync in current releases.** Data stays on the machine where it was
  created unless you explicitly export or back it up to a location you choose.

Optional account-based synchronization and online backup are planned future
features. If introduced, they will be opt-in, core local task management will
continue to work without an account, and this policy will be updated before the
features become available.

## Network usage

SchedPlus itself uses the network only to check for application updates in
supported packages. These checks fetch signed release metadata and verified
packages from GitHub over HTTPS. Snap and Microsoft Store installations use
their provider's update service instead. No task data is included in update
checks.

You can disable automatic update checks at any time in Settings > General.

## Data locations

| Platform | Default database location |
| --- | --- |
| Linux | `~/.local/share/ZFordDev/SchedPlus/tasks.db` |
| macOS | `~/Library/Application Support/ZFordDev/SchedPlus/tasks.db` |
| Windows | `%APPDATA%\ZFordDev\SchedPlus\tasks.db` |
| Snap | `$SNAP_USER_COMMON/SchedPlus/tasks.db` |

You can view the exact database path in Settings > Data.

## Backup and export

- **Backups** are complete JSON files containing all tasks and preferences.
- **Exports** are task-only JSON files without settings.
- Both formats are human-readable and can be inspected or edited manually.
- Backups and exports are never uploaded by SchedPlus.

## Third-party dependencies

SchedPlus's core logic is open-source under Apache 2.0. The desktop
application shell is GPL-3.0. All dependencies retain their original licenses.
See [NOTICE](NOTICE) for details.

## Contact

For privacy questions, open an issue at
[github.com/ZFordDev/SchedPlus/issues](https://github.com/ZFordDev/SchedPlus/issues)
or review the source code directly.
