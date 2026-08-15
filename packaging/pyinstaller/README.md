# PyInstaller build profiles

Each `.spec` creates a reproducible **onedir** frozen directory. Build a
profile only in an environment that has its matching runtime dependencies:

```bash
pip install pyinstaller
pip install -e ".[standard]"  # or .[lite], .[full], or the base package for CLI
pyinstaller --noconfirm packaging/pyinstaller/schedplus-standard.spec
```

| Profile | Output directory | Launcher | Excluded frameworks |
| --- | --- | --- | --- |
| Standard | `SchedPlusStandard/` | PyQt | Tkinter and tkcalendar |
| Lite | `SchedPlusLite/` | Tkinter | PyQt6 |
| Full | `SchedPlusFull/` | interface selector | none |
| CLI | `SchedPlusCli/` | command parser | PyQt6, Tkinter, tkcalendar |

Every frozen directory bundles the application icon, all PNG icon sizes, Linux
desktop/AppStream metadata, `LICENSE`, `LICENSES/`, and `NOTICE`. The frozen
directory is an internal package format; a Debian package, AppImage, Snap,
Windows installer, or Store package wraps it later.

Every profile explicitly collects the shared updater modules required during
startup and package-identity loading. Embedded build policy still decides
whether a particular package is internally or externally updated.

## GPL source obligations

SchedPlus desktop distributions are GPL-3.0-only. When distributing any frozen
edition, provide the corresponding source under GPL-3.0-only and retain the
bundled `LICENSE` and `NOTICE`. Publish the matching source tag or source
archive alongside each binary release, and link to
<https://github.com/ZFordDev/SchedPlus>. The separately reusable `src/logic/`
modules remain Apache-2.0; preserve `LICENSES/Apache-2.0.txt`. Releases through
0.7.3 had a blanket MIT license, whose historical text and attribution remain
in `LICENSES/MIT.txt` and `NOTICE`.

Run `python scripts/validate_frozen_artifact.py --edition standard --directory
dist/SchedPlusStandard` after each build. CI builds and validates all profiles
on Windows; the CLI executable is also run with `--help` as a frozen smoke test.
