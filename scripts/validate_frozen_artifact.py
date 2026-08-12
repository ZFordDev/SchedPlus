"""Validate that a PyInstaller onedir artifact contains only its edition assets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


EDITION_CONFIG = {
    "standard": {"directory": "SchedPlusStandard", "forbidden": ("tkinter", "tkcalendar")},
    "lite": {"directory": "SchedPlusLite", "forbidden": ("PyQt6",)},
    "full": {"directory": "SchedPlusFull", "forbidden": ()},
    "cli": {"directory": "SchedPlusCli", "forbidden": ("PyQt6", "tkinter", "tkcalendar")},
}
REQUIRED_SUFFIXES = (
    "assets/windows/SchedPlus.ico",
    "assets/icons/icon-512.png",
    "packaging/metadata/dev.zford.SchedPlus.desktop",
    "packaging/metadata/dev.zford.SchedPlus.metainfo.xml",
    "licenses/LICENSE",
    "licenses/LICENSES/Apache-2.0.txt",
    "licenses/LICENSES/MIT.txt",
    "licenses/NOTICE",
)


def validate(directory: Path, edition: str) -> list[str]:
    errors = []
    config = EDITION_CONFIG[edition]
    if directory.name != config["directory"]:
        errors.append(f"expected {config['directory']!r} directory, got {directory.name!r}")
    if not directory.is_dir():
        return [*errors, f"artifact directory does not exist: {directory}"]

    paths = tuple(path.as_posix() for path in directory.rglob("*") if path.is_file())
    if not any(path.endswith(".exe") or "/" not in path for path in paths):
        errors.append("onedir artifact has no launcher executable")
    for suffix in REQUIRED_SUFFIXES:
        if not any(path.endswith(suffix) for path in paths):
            errors.append(f"artifact is missing bundled {suffix}")
    for forbidden in config["forbidden"]:
        if any(forbidden.casefold() in path.casefold() for path in paths):
            errors.append(f"{edition} artifact unexpectedly includes {forbidden}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", choices=EDITION_CONFIG, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    options = parser.parse_args()
    errors = validate(options.directory, options.edition)
    if errors:
        print("Frozen artifact validation failed:", *errors, sep="\n- ", file=sys.stderr)
        return 1
    print(f"{options.edition} frozen artifact validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
