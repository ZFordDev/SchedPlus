# Post-release smoke-test and stable-promotion checklist

Run the **Post-release installation and upgrade smoke tests** workflow against
the draft release tag. Leave **promote_stable** disabled for the first run. The
mandatory automated matrix must pass for Debian Standard, Lite, and CLI;
AppImage Standard; all four Windows portable editions; the Windows Standard
installer; and Store updater policy. Review the sanitized log artifacts, then
rerun with **promote_stable** enabled to publish a `release-*` draft. The
promotion job cannot run unless every mandatory job succeeds.

The automated upgrade starts with a populated v0.8.0 schema-zero database. It
launches the candidate, verifies the database reached the current schema and
the known task survived, removes application files, and verifies user data
remains. Portable Windows artifacts and the installed Windows build use
separate jobs. Logs redact home, runner, workspace, and secret-like values;
never upload an original application data directory or raw task database.

## Manual checks for real hosts and Stores

- On Windows 10 and 11, verify the Authenticode signature and timestamp, install
  through the visible wizard, inspect Start Menu and uninstall entries, upgrade
  an actual v0.8.0 install, and confirm SmartScreen behavior.
- Install the Partner Center-signed MSIX from Microsoft Store flighting. Confirm
  task persistence across a Store update and confirm **Check for updates** is
  externally managed and never launches the internal updater.
- Install the staged Snap on a system with working snapd confinement. Add a
  task, refresh from `edge` to `candidate`, verify `$SNAP_USER_COMMON` data, and
  confirm updates remain Snap Store-managed.
- Run the AppImage with FUSE on at least one current Debian-family and one
  non-Debian distribution. Check desktop integration, file dialogs, backup and
  restore, and the documented extraction fallback.
- Visually inspect PyQt Standard, Tkinter Lite, and Full selection on native
  displays, including scaling, menus, calendar interaction, and shutdown.
- Exercise a signed preview update on a disposable managed portable install,
  including download verification, restart health confirmation, and rollback.
- Uninstall each installed package and confirm application files are removed
  while `tasks.db`, preferences, backups, and user-selected exports remain.
- Inspect sanitized CI logs for useful diagnostics and confirm they contain no
  signing values, credentials, usernames, home paths, or private task text.

Record the workflow run URL and manual results in the release notes or release
tracking issue before stable promotion. Failures require a new candidate; do
not promote by bypassing the workflow.
