# SchedPlus Standard Snap

The registered Store name is `schedplus`. The committed `snap/snapcraft.yaml`
builds only the Standard PyQt edition under strict confinement and installs the
desktop entry and icon from `snap/gui/`.

The Snap icon is the current 256px release icon copied from
`assets/icons/icon-256.png`; the obsolete source SVG is not used.

Build from the repository root with:

```bash
python3 scripts/sync_release_versions.py
snapcraft --use-lxd
```

CI runs the same version-sync helper immediately before building, so the
package version always comes from `pyproject.toml`. The rest of the committed
manifest is never generated dynamically.

For local testing on a supported clean Ubuntu system:

```bash
sudo snap install --dangerous ./schedplus_*.snap
snap run schedplus
```

CI builds the Snap and inspects its packaged identity, confinement, desktop
entry, and icon. Install, graphical launch, and Store-refresh persistence are
tested manually on a supported Snap host: unsigned local snaps can be installed
with `--dangerous`, but snapd cannot exercise a Store refresh from that same
unasserted artifact.

SchedPlus stores its database at
`$SNAP_USER_COMMON/SchedPlus/tasks.db` (`~/snap/schedplus/common/SchedPlus/tasks.db`
for a normal per-user installation). `SNAP_USER_COMMON` is shared by all
revisions, so automatic refreshes preserve tasks. The package requests `home`
for user-selected files; the GNOME extension supplies the desktop, Wayland,
X11, settings, theme, and OpenGL interfaces needed by PyQt.

## Build service and publishing policy

The Snap Store is linked directly to `ZFordDev/SchedPlus` and uses Canonical's
build service. GitHub Actions independently builds an amd64 candidate for the
unified draft Release, but it holds no Snap Store credentials and never
publishes a Store revision.

After every platform artifact has passed and the draft GitHub Release exists,
release the corresponding Canonical-built revision manually in the Snapcraft
dashboard: trial prereleases go to `edge`, release candidates to `candidate`,
and production releases are promoted to `stable` only after final approval.
The manifest currently limits Store builds to amd64, the architecture tested
by the release workflow.
