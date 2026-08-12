"""Verify the unified release payload before creating a draft release."""

from __future__ import annotations

import argparse
import sys
import tarfile
import zipfile
from pathlib import Path

WINDOWS_EDITIONS = ("Standard", "Lite", "Full", "CLI")


def validate(directory: Path, version: str) -> list[str]:
    errors: list[str] = []
    files = tuple(path for path in directory.iterdir() if path.is_file())
    names = {path.name for path in files}

    required_patterns = (
        f"SchedPlus-{version}-*.AppImage",
        f"schedplus_{version}_*.deb",
        f"schedplus-lite_{version}_*.deb",
        f"schedplus-cli_{version}_*.deb",
        f"schedplus_{version}_*.snap",
        f"SchedPlus-Setup-{version}-windows-x86_64.exe",
        f"SchedPlus-{version}-source.tar.gz",
    )
    for pattern in required_patterns:
        if not tuple(directory.glob(pattern)):
            errors.append(f"missing release artifact matching {pattern}")
    for edition in WINDOWS_EDITIONS:
        pattern = f"SchedPlus-{edition}-{version}-windows-x86_64.zip"
        if pattern not in names:
            errors.append(f"missing release artifact {pattern}")

    for archive in directory.glob("*.zip"):
        with zipfile.ZipFile(archive) as source:
            members = source.namelist()
        for required in ("licenses/LICENSE", "licenses/NOTICE"):
            if not any(member.endswith(required) for member in members):
                errors.append(f"{archive.name} is missing {required}")
        if ("-Lite-" in archive.name or "-CLI-" in archive.name) and any(
            "pyqt6" in member.casefold() for member in members
        ):
            errors.append(f"{archive.name} unexpectedly contains PyQt6")

    source_archives = tuple(directory.glob("*-source.tar.gz"))
    for archive in source_archives:
        with tarfile.open(archive, "r:gz") as source:
            members = source.getnames()
        for required in ("LICENSE", "NOTICE", "LICENSES/Apache-2.0.txt", "LICENSES/MIT.txt"):
            if not any(member.endswith(f"/{required}") for member in members):
                errors.append(f"{archive.name} is missing {required}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--version", required=True)
    options = parser.parse_args()
    errors = validate(**vars(options))
    if errors:
        print("Release artifact verification failed:", *errors, sep="\n- ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
