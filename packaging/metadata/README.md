# SchedPlus package metadata and release assets

This directory is the single source of shared release identity for Debian,
AppImage, Snap, Windows installers, and Microsoft Store submissions.

## Identity and branding

| Purpose | Value |
| --- | --- |
| Display name | SchedPlus |
| Stable application ID | `dev.zford.SchedPlus` |
| Linux desktop ID | `dev.zford.SchedPlus.desktop` |
| AppStream component ID | `dev.zford.SchedPlus` |
| Windows application/user model ID | `dev.zford.SchedPlus` |
| Debian package and Snap name | `schedplus` |
| Full desktop command | `schedplus-full` |

Use this description in package catalogs: **“A modern, local-first scheduler for planning tasks and time without an account or network connection.”**

## Linux assets

Install `dev.zford.SchedPlus.desktop` to
`/usr/share/applications/` and `dev.zford.SchedPlus.metainfo.xml` to
`/usr/share/metainfo/`. Install the PNG files in `assets/icons/` as
`/usr/share/icons/hicolor/<size>x<size>/apps/dev.zford.SchedPlus.png`.
The desktop entry launches the Full edition selector; edition-specific packages
may replace `Exec` with their dedicated command.

## Windows and Store assets

`assets/windows/SchedPlus.ico` contains the 16, 24, 32, 48, 64, 128, and 256
pixel application images required by typical Windows installers. It is generated
from the identically sized PNG sources in `assets/icons/`; run
`python scripts/generate_release_assets.py` after changing those source icons.

Microsoft Store packaging must supply unplated PNG logo assets at these sizes
(scale variants can be generated from the 512px master):

| Asset | Required base size |
| --- | --- |
| Square44x44Logo | 44 × 44 |
| Square71x71Logo | 71 × 71 |
| Square150x150Logo | 150 × 150 |
| Square310x310Logo | 310 × 310 |
| Wide310x150Logo | 310 × 150 |
| StoreLogo | 50 × 50 |

The MSIX build generates the final package-specific PNGs from the 512px master
into its staging directory; see [../msix/README.md](../msix/README.md). They
must use the Partner Center identity and current SchedPlus branding.

## Licensing and source disclosure

Copyright © 2026 ZFordDev and SchedPlus contributors. The complete desktop
application is GPL-3.0-only ([LICENSE](../../LICENSE)); reusable modules in
`src/logic/` are Apache-2.0 ([LICENSES/Apache-2.0.txt](../../LICENSES/Apache-2.0.txt)).
The historical MIT text remains at [LICENSES/MIT.txt](../../LICENSES/MIT.txt),
and the licensing boundary, attribution, and final blanket-MIT release are
explained in [NOTICE](../../NOTICE). Package metadata and store listings must
link to the source repository: <https://github.com/ZFordDev/SchedPlus>.

## Validation

Run `python scripts/validate_release_metadata.py` locally. CI runs the same
validation for changes to release metadata, icons, or the validator.
