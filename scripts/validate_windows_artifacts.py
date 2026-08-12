"""Validate the portable and installer artifacts created for Windows releases."""

from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

try:
    from .build_windows_packages import EDITIONS, ARCHITECTURE, _portable_name
except ImportError:  # Direct execution: ``python scripts/validate_windows_artifacts.py``.
    from build_windows_packages import EDITIONS, ARCHITECTURE, _portable_name


def validate(output_dir: Path, version: str) -> list[str]:
    """Return a list of missing or malformed release artifact diagnostics."""
    errors: list[str] = []
    expected = []
    for edition in EDITIONS:
        filename = f"{_portable_name(edition, version)}.zip"
        expected.append(filename)
        path = output_dir / filename
        if not path.is_file():
            errors.append(f"missing portable artifact: {filename}")
            continue
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
        root = _portable_name(edition, version)
        if f"{root}/SOURCE.txt" not in names:
            errors.append(f"{filename} does not include SOURCE.txt")

    installer = f"SchedPlus-Setup-{version}-windows-{ARCHITECTURE}.exe"
    expected.append(installer)
    if not (output_dir / installer).is_file():
        errors.append(f"missing installer artifact: {installer}")

    checksum = output_dir / "SHA256SUMS.txt"
    if not checksum.is_file():
        return errors + ["missing SHA256SUMS.txt"]
    recorded = {
        filename: digest
        for digest, filename in (
            line.split(" *", 1)
            for line in checksum.read_text(encoding="utf-8").splitlines()
            if " *" in line
        )
    }
    for filename in expected:
        artifact = output_dir / filename
        if filename not in recorded:
            errors.append(f"checksum missing for {filename}")
        elif artifact.is_file() and recorded[filename] != hashlib.sha256(artifact.read_bytes()).hexdigest():
            errors.append(f"checksum mismatch for {filename}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--version", required=True)
    options = parser.parse_args()
    errors = validate(**vars(options))
    if errors:
        print("\n".join(errors))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
