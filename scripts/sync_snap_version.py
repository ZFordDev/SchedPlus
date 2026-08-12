"""Set the committed Snapcraft manifest version from project metadata."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sync_version(*, project_file: Path, manifest: Path) -> str:
    with project_file.open("rb") as source:
        version = tomllib.load(source)["project"]["version"]

    content = manifest.read_text(encoding="utf-8")
    updated, replacements = re.subn(
        r'(?m)^version:\s*[^\n]+$', f'version: "{version}"', content, count=1
    )
    if replacements != 1:
        raise ValueError(f"expected exactly one top-level version field in {manifest}")
    manifest.write_text(updated, encoding="utf-8")
    return version


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-file", type=Path, default=PROJECT_ROOT / "pyproject.toml")
    parser.add_argument("--manifest", type=Path, default=PROJECT_ROOT / "snap" / "snapcraft.yaml")
    options = parser.parse_args()
    print(sync_version(**vars(options)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
