# Debian packages

Build the `schedplus` (Standard), `schedplus-lite`, or `schedplus-cli` package
from its matching PyInstaller onedir artifact:

```bash
VERSION="$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")"
python scripts/build_debian_package.py \
  --edition standard \
  --frozen-dir dist/SchedPlusStandard \
  --output-dir artifacts/debian \
  --version "$VERSION"
```

Packages install the frozen application under `/usr/lib/<package>/` and a small
launcher under `/usr/bin/`. Standard and Lite install the desktop entry,
hicolor icons, and AppStream metadata. All editions install `LICENSE`,
`LICENSES/`, `NOTICE`, `CHANGELOG.md`, and Debian copyright information under
`/usr/share/doc/<package>/`.

The editions are deliberately mutually exclusive (`Conflicts` and `Replaces`
are declared in package control metadata) because Standard and Lite share a
desktop ID while presenting different interfaces. No maintainer scripts create,
change, or remove user data. SchedPlus therefore continues to use
`~/.local/share/ZFordDev/SchedPlus/tasks.db`, which survives upgrades and
package removal.

Artifacts are consistently named `<package>_<version>_<architecture>.deb`; the
architecture comes from `dpkg --print-architecture`, not a hard-coded value.
CI runs `lintian --fail-on error`, installs each package on a clean runner,
removes it, and verifies the pre-existing user database remains untouched.

PyInstaller intentionally embeds an upstream Python runtime and extension
libraries. The packages normalize shared-library permissions and fix ordinary
Debian metadata issues directly. The remaining unavoidable lintian findings
(embedded runtime libraries, their upstream RUNPATH, stripping and dependency
analysis) are listed in package-specific overrides under
`/usr/share/lintian/overrides/`. They are explicit exceptions, not ignored CI.

Tagged release packages embed their edition, architecture, channel, signed
manifest URL, and verification key. SchedPlus can download and verify the exact
matching `.deb`, then opens its location for installation with the user's normal
APT or desktop package tools; it never attempts privileged installation itself.
