"""Set derived package versions from authoritative project metadata."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _replace_once(content: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, content, count=1, flags=re.MULTILINE)
    if count != 1:
        raise ValueError(f"expected exactly one {label}")
    return updated


def sync_versions(*, project_file: Path, snap_manifest: Path, windows_version: Path) -> str:
    with project_file.open("rb") as source:
        version = tomllib.load(source)["project"]["version"]

    manifest = _replace_once(
        snap_manifest.read_text(encoding="utf-8"),
        r"^version:\s*[^\n]+$",
        f'version: "{version}"',
        f"top-level version field in {snap_manifest}",
    )
    snap_manifest.write_text(manifest, encoding="utf-8")

    components = version.split(".")
    if not components or any(not item.isdigit() for item in components) or len(components) > 4:
        raise ValueError(f"Windows package version must contain one to four numeric fields: {version}")
    numeric = ", ".join([*components, *(["0"] * (4 - len(components)))])
    resource = windows_version.read_text(encoding="utf-8")
    for field in ("filevers", "prodvers"):
        resource = _replace_once(resource, rf"^\s*{field}=\([^\n]+\),$", f"    {field}=({numeric}),", field)
    for field in ("FileVersion", "ProductVersion"):
        resource = _replace_once(
            resource,
            rf"StringStruct\('{field}', '[^']+'\)",
            f"StringStruct('{field}', '{version}')",
            field,
        )
    windows_version.write_text(resource, encoding="utf-8")
    return version


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-file", type=Path, default=PROJECT_ROOT / "pyproject.toml")
    parser.add_argument("--snap-manifest", type=Path, default=PROJECT_ROOT / "snap" / "snapcraft.yaml")
    parser.add_argument(
        "--windows-version",
        type=Path,
        default=PROJECT_ROOT / "packaging" / "pyinstaller" / "version_info.txt",
    )
    options = parser.parse_args()
    print(sync_versions(**vars(options)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
