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

The Snap is publicly available under the registered Store name `schedplus`.
GitHub Actions builds amd64 revisions and publishes them with
`SNAPCRAFT_STORE_CREDENTIALS` according to the source event:

- meaningful package or application changes on `main` publish to `edge`;
- `pre-release-*` tags publish to `candidate`; and
- `release-*` tags publish to `stable`.

The edge workflow is limited to named application and packaging paths, so
unrelated repository changes do not trigger it. Manual dispatch builds and
validates an artifact but does not publish it. The unified GitHub Release
workflow also builds a Snap artifact for its release payload without publishing
that artifact to the Snap Store.
