"""Generate the Windows multi-resolution icon from committed PNG source icons."""

from __future__ import annotations

import struct
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ICON_DIRECTORY = PROJECT_ROOT / "assets" / "icons"
OUTPUT = PROJECT_ROOT / "assets" / "windows" / "SchedPlus.ico"
SIZES = (16, 24, 32, 48, 64, 128, 256)


def png_dimensions(source: bytes) -> tuple[int, int]:
    if source[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("source is not a PNG")
    return struct.unpack(">II", source[16:24])


def generate() -> Path:
    images = []
    for size in SIZES:
        source = (ICON_DIRECTORY / f"icon-{size}.png").read_bytes()
        if png_dimensions(source) != (size, size):
            raise ValueError(f"icon-{size}.png must be {size}x{size}")
        images.append((size, source))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    offset = 6 + 16 * len(images)
    directory = bytearray()
    payload = bytearray()
    for size, source in images:
        encoded_size = 0 if size == 256 else size
        directory.extend(
            struct.pack("<BBBBHHII", encoded_size, encoded_size, 0, 0, 1, 32, len(source), offset)
        )
        payload.extend(source)
        offset += len(source)

    OUTPUT.write_bytes(struct.pack("<HHH", 0, 1, len(images)) + directory + payload)
    return OUTPUT


if __name__ == "__main__":
    print(generate())
