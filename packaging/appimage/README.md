# SchedPlus Standard AppImage

SchedPlus provides a portable AppImage for the Standard (PyQt) edition only.
It is built from the `SchedPlusStandard` PyInstaller onedir artifact and uses
an AppDir with `AppRun`, `dev.zford.SchedPlus.desktop`, and the application
icon at its root. The frozen payload is installed under `usr/lib/schedplus/`
inside the AppDir.

```bash
python scripts/build_appimage.py \
  --frozen-dir dist/SchedPlusStandard \
  --output-dir artifacts/appimage \
  --version 0.8.1 \
  --appimagetool ./appimagetool-x86_64.AppImage
```

The artifact is named `SchedPlus-<version>-<architecture>.AppImage`, with a
neighbouring `.sha256` checksum file. CI builds on Ubuntu 22.04, the oldest
currently supported GitHub-hosted Linux build base for this project, to keep
the portable runtime compatible with supported Linux distributions. The build
uses appimagetool's supported `zstd` compression.

## Running and troubleshooting

Make the file executable and run it directly:

```bash
chmod +x SchedPlus-*.AppImage
./SchedPlus-*.AppImage
```

AppImage normally requires FUSE (often provided by the `libfuse2` package).
When FUSE is unavailable, extract and run without mounting the image:

```bash
./SchedPlus-*.AppImage --appimage-extract
./squashfs-root/AppRun
```

The AppImage bundles SchedPlus and its PyQt runtime. It still uses the host's
standard graphics stack (including EGL/OpenGL libraries such as `libegl1` and
`libgl1`), which is normally present on supported desktop Linux distributions.
The release smoke test uses Qt's `offscreen` platform plugin so it validates the
portable application without coupling the build to a particular X11/XCB stack.

The AppImage is read-only at runtime. SchedPlus stores tasks outside the image
at `~/.local/share/ZFordDev/SchedPlus/tasks.db`; it never needs write access to
the directory containing the AppImage. A Lite AppImage is intentionally not
provided unless there is demonstrated demand.

Tagged release AppImages embed the stable or preview signed-manifest identity.
SchedPlus verifies the matching AppImage's signed SHA-256 and byte size before
opening its download location. Replacing or relaunching an AppImage remains an
explicit user action.
