"""Build a release-grade Debian package from one PyInstaller onedir artifact."""

from __future__ import annotations

import argparse
import gzip
import shutil
import subprocess
import sys  # Imported for command-line entry-point tests.
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts.update_release_metadata import embed_packaged_build_info
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from update_release_metadata import embed_packaged_build_info


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA = PROJECT_ROOT / "packaging" / "metadata"
DESCRIPTION = "Modern local-first scheduler for planning tasks and time"


@dataclass(frozen=True)
class Edition:
    name: str
    frozen_name: str
    launcher: str
    executable: str
    desktop: bool

    @property
    def conflicts(self) -> tuple[str, ...]:
        return tuple(item.name for item in EDITIONS.values() if item.name != self.name)


EDITIONS = {
    "standard": Edition("schedplus", "SchedPlusStandard", "schedplus", "SchedPlusStandard", True),
    "lite": Edition("schedplus-lite", "SchedPlusLite", "schedplus-lite", "SchedPlusLite", True),
    "cli": Edition("schedplus-cli", "SchedPlusCli", "schedplus-cli", "SchedPlusCli", False),
}


def _architecture() -> str:
    return subprocess.check_output(["dpkg", "--print-architecture"], text=True).strip()


def _write(path: Path, content: str, *, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def _control(edition: Edition, version: str, architecture: str) -> str:
    conflicts = ", ".join(edition.conflicts)
    return f"""Package: {edition.name}
Version: {version}
Section: utils
Priority: optional
Architecture: {architecture}
Maintainer: ZFordDev <zforddev@gmail.com>
Conflicts: {conflicts}
Replaces: {conflicts}
Description: {DESCRIPTION}
 SchedPlus is an offline-friendly task scheduler with SQLite persistence.
 This package contains the {edition.name} edition.
"""


def _copyright() -> str:
    return """Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: SchedPlus
Source: https://github.com/ZFordDev/SchedPlus

Files: *
Copyright: 2026 ZFordDev and SchedPlus contributors
License: GPL-3.0-only

Files: src/logic/*
Copyright: 2026 ZFordDev and SchedPlus contributors
License: Apache-2.0

License: GPL-3.0-only
 The complete license text is installed as /usr/share/doc/schedplus/LICENSE.

License: Apache-2.0
 On Debian systems, the complete text of the Apache License, Version 2.0 can
 be found in /usr/share/common-licenses/Apache-2.0. A copy is also retained in
 /usr/share/doc/schedplus/LICENSES/Apache-2.0.txt for source-distribution
 attribution.
"""


def _lintian_overrides(package: str) -> str:
    """Document policy exceptions inherent in an upstream PyInstaller runtime."""
    return "\n".join(
        f"""{package}: custom-library-search-path
{package}: embedded-library
{package}: library-not-linked-against-libc
{package}: unstripped-binary-or-object
{package}: shared-library-lacks-prerequisites
{package}: undeclared-elf-prerequisites
{package}: hardening-no-pie
{package}: shared-library-is-executable""".splitlines()
    ) + "\n"


def _normalize_shared_library_modes(application_dir: Path) -> None:
    """Shared objects are data loaded by the frozen runtime, not executables."""
    for candidate in application_dir.rglob("*.so*"):
        candidate.chmod(candidate.stat().st_mode & ~0o111)


def build(*, edition: str, frozen_dir: Path, output_dir: Path, version: str) -> Path:
    edition = EDITIONS[edition]
    frozen_dir = frozen_dir.resolve()
    if frozen_dir.name != edition.frozen_name:
        raise ValueError(f"{edition.name} requires {edition.frozen_name!r} frozen directory")
    if not frozen_dir.is_dir():
        raise ValueError(f"frozen directory does not exist: {frozen_dir}")

    architecture = _architecture()
    stage = output_dir / f"{edition.name}-{architecture}"
    if stage.exists():
        shutil.rmtree(stage)
    application_dir = stage / "usr" / "lib" / edition.name
    shutil.copytree(frozen_dir, application_dir)
    embed_packaged_build_info(
        application_dir,
        version=version,
        edition={"schedplus": "standard", "schedplus-lite": "lite", "schedplus-cli": "cli"}[edition.name],
        platform="linux",
        architecture=architecture,
        package_format="deb",
    )
    _normalize_shared_library_modes(application_dir)

    _write(stage / "DEBIAN" / "control", _control(edition, version, architecture))
    _write(
        stage / "usr" / "bin" / edition.launcher,
        f"#!/bin/sh\nexec /usr/lib/{edition.name}/{edition.executable} \"$@\"\n",
        executable=True,
    )

    if edition.desktop:
        desktop = (METADATA / "dev.zford.SchedPlus.desktop").read_text(encoding="utf-8")
        desktop = desktop.replace("Exec=schedplus-full", f"Exec={edition.launcher}")
        _write(stage / "usr" / "share" / "applications" / "dev.zford.SchedPlus.desktop", desktop)
        metainfo = stage / "usr" / "share" / "metainfo" / "dev.zford.SchedPlus.metainfo.xml"
        metainfo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(METADATA / "dev.zford.SchedPlus.metainfo.xml", metainfo)
        for icon in (PROJECT_ROOT / "assets" / "icons").glob("icon-*.png"):
            size = icon.stem.removeprefix("icon-")
            destination = stage / "usr" / "share" / "icons" / "hicolor" / f"{size}x{size}" / "apps" / "dev.zford.SchedPlus.png"
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(icon, destination)

    documents = stage / "usr" / "share" / "doc" / edition.name
    documents.mkdir(parents=True, exist_ok=True)
    for source in (PROJECT_ROOT / "LICENSE", PROJECT_ROOT / "NOTICE"):
        shutil.copy2(source, documents / source.name)
    with (PROJECT_ROOT / "CHANGELOG.md").open("rb") as source, gzip.GzipFile(
        documents / "changelog.gz", "wb", mtime=0
    ) as destination:
        shutil.copyfileobj(source, destination)
    shutil.copytree(PROJECT_ROOT / "LICENSES", documents / "LICENSES")
    _write(documents / "copyright", _copyright())
    _write(
        stage / "usr" / "share" / "lintian" / "overrides" / edition.name,
        _lintian_overrides(edition.name),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / f"{edition.name}_{version}_{architecture}.deb"
    subprocess.run(["dpkg-deb", "--build", "--root-owner-group", str(stage), str(artifact)], check=True)
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edition", choices=EDITIONS, required=True)
    parser.add_argument("--frozen-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--version", required=True)
    options = parser.parse_args()
    print(build(**vars(options)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
