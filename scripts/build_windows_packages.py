"""Create Windows portable ZIPs, the Standard installer, and SHA-256 checksums."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WINDOWS_PACKAGING = PROJECT_ROOT / "packaging" / "windows"
ARCHITECTURE = "x86_64"


@dataclass(frozen=True)
class Edition:
    key: str
    frozen_directory: str
    display_name: str


EDITIONS = (
    Edition("standard", "SchedPlusStandard", "Standard"),
    Edition("lite", "SchedPlusLite", "Lite"),
    Edition("full", "SchedPlusFull", "Full"),
    Edition("cli", "SchedPlusCli", "CLI"),
)


def _source_info(directory: Path) -> None:
    shutil.copy2(WINDOWS_PACKAGING / "SOURCE.txt", directory / "SOURCE.txt")


def _portable_name(edition: Edition, version: str) -> str:
    return f"SchedPlus-{edition.display_name}-{version}-windows-{ARCHITECTURE}"


def build_portables(*, frozen_root: Path, output_dir: Path, version: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for edition in EDITIONS:
        frozen = frozen_root / edition.frozen_directory
        if not frozen.is_dir():
            raise ValueError(f"missing {edition.key} frozen directory: {frozen}")
        staging = output_dir / _portable_name(edition, version)
        if staging.exists():
            shutil.rmtree(staging)
        shutil.copytree(frozen, staging)
        _source_info(staging)
        archive = shutil.make_archive(str(staging), "zip", output_dir, staging.name)
        shutil.rmtree(staging)
        artifacts.append(Path(archive))
    return artifacts


def build_installer(*, frozen_root: Path, output_dir: Path, version: str, iscc: Path) -> Path:
    frozen = (frozen_root / "SchedPlusStandard").resolve()
    if not frozen.is_dir():
        raise ValueError(f"missing standard frozen directory: {frozen}")
    output_dir.mkdir(parents=True, exist_ok=True)
    environment = {
        **os.environ,
        "SCHEDPLUS_VERSION": version,
        "SCHEDPLUS_FROZEN_DIR": str(frozen),
        "SCHEDPLUS_OUTPUT_DIR": str(output_dir.resolve()),
    }
    subprocess.run([str(iscc.resolve()), str(WINDOWS_PACKAGING / "SchedPlus.iss")], check=True, env=environment)
    artifact = output_dir / f"SchedPlus-Setup-{version}-windows-{ARCHITECTURE}.exe"
    if not artifact.is_file():
        raise RuntimeError(f"Inno Setup did not create {artifact}")
    return artifact


def write_checksums(artifacts: list[Path], output_dir: Path) -> Path:
    checksum = output_dir / "SHA256SUMS.txt"
    lines = []
    for artifact in sorted(artifacts):
        with artifact.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        lines.append(f"{digest} *{artifact.name}")
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksum


def build(*, frozen_root: Path, output_dir: Path, version: str, iscc: Path) -> list[Path]:
    artifacts = build_portables(frozen_root=frozen_root, output_dir=output_dir, version=version)
    artifacts.append(build_installer(frozen_root=frozen_root, output_dir=output_dir, version=version, iscc=iscc))
    artifacts.append(write_checksums(artifacts, output_dir))
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--iscc", type=Path, required=True)
    options = parser.parse_args()
    print(*build(**vars(options)), sep="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
