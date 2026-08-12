"""Validate release identity, metadata, icons, and required licensing references."""

from __future__ import annotations

import struct
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA = PROJECT_ROOT / "packaging" / "metadata"
APPLICATION_ID = "dev.zford.SchedPlus"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256, 512)
WINDOWS_ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def _png_dimensions(path: Path) -> tuple[int, int]:
    source = path.read_bytes()
    if source[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", source[16:24])


def _ico_sizes(path: Path) -> tuple[int, ...]:
    source = path.read_bytes()
    reserved, image_type, count = struct.unpack("<HHH", source[:6])
    if (reserved, image_type) != (0, 1):
        raise ValueError(f"{path} is not an ICO file")
    sizes = []
    for index in range(count):
        width, height = source[6 + index * 16 : 8 + index * 16]
        if width != height:
            raise ValueError(f"{path} contains a non-square image")
        sizes.append(width or 256)
    return tuple(sizes)


def validate() -> list[str]:
    errors = []
    desktop = METADATA / f"{APPLICATION_ID}.desktop"
    appstream = METADATA / f"{APPLICATION_ID}.metainfo.xml"
    readme = METADATA / "README.md"

    desktop_text = desktop.read_text(encoding="utf-8")
    for value in (
        "[Desktop Entry]",
        "Type=Application",
        "Name=SchedPlus",
        "Exec=schedplus-full",
        f"Icon={APPLICATION_ID}",
        "Categories=Office;Calendar;Utility;",
    ):
        if value not in desktop_text:
            errors.append(f"desktop entry is missing {value!r}")

    try:
        root = ElementTree.parse(appstream).getroot()
        values = {child.tag: child.text for child in root}
        if root.attrib.get("type") != "desktop-application":
            errors.append("AppStream component must be a desktop application")
        for tag, expected in (("id", APPLICATION_ID), ("name", "SchedPlus"), ("project_license", "GPL-3.0-only")):
            if values.get(tag) != expected:
                errors.append(f"AppStream {tag} must be {expected!r}")
    except ElementTree.ParseError as exc:
        errors.append(f"AppStream XML is invalid: {exc}")

    for size in ICON_SIZES:
        path = PROJECT_ROOT / "assets" / "icons" / f"icon-{size}.png"
        if not path.exists() or _png_dimensions(path) != (size, size):
            errors.append(f"missing valid {size}x{size} PNG icon")

    ico = PROJECT_ROOT / "assets" / "windows" / "SchedPlus.ico"
    if not ico.exists() or _ico_sizes(ico) != WINDOWS_ICON_SIZES:
        errors.append("Windows ICO must contain 16, 24, 32, 48, 64, 128, and 256px images")

    package_readme = readme.read_text(encoding="utf-8")
    for value in ("GPL-3.0-only", "Apache-2.0", "MIT", "NOTICE", "github.com/ZFordDev/SchedPlus", "Square44x44Logo"):
        if value not in package_readme:
            errors.append(f"metadata documentation is missing {value!r}")

    for path in (PROJECT_ROOT / "LICENSE", PROJECT_ROOT / "LICENSES" / "Apache-2.0.txt", PROJECT_ROOT / "LICENSES" / "MIT.txt", PROJECT_ROOT / "NOTICE"):
        if not path.is_file():
            errors.append(f"required licensing file is missing: {path.name}")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        print("Release metadata validation failed:", *failures, sep="\n- ", file=sys.stderr)
        raise SystemExit(1)
    print("Release metadata validation passed.")
