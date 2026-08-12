"""Create a portable Standard-edition AppImage from a PyInstaller onedir build."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA = PROJECT_ROOT / "packaging" / "metadata"
FROZEN_NAME = "SchedPlusStandard"
APPLICATION_ID = "dev.zford.SchedPlus"


def architecture() -> str:
    machine = subprocess.check_output(["uname", "-m"], text=True).strip()
    return {"amd64": "x86_64", "x86_64": "x86_64", "aarch64": "aarch64"}.get(machine, machine)


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def create_appdir(*, frozen_dir: Path, appdir: Path) -> Path:
    frozen_dir = frozen_dir.resolve()
    if frozen_dir.name != FROZEN_NAME:
        raise ValueError(f"AppImage requires the {FROZEN_NAME!r} frozen directory")
    if not frozen_dir.is_dir():
        raise ValueError(f"frozen directory does not exist: {frozen_dir}")
    if appdir.exists():
        shutil.rmtree(appdir)

    application_dir = appdir / "usr" / "lib" / "schedplus"
    shutil.copytree(frozen_dir, application_dir)
    _write(
        appdir / "AppRun",
        "#!/bin/sh\nexec \"$(dirname \"$0\")/usr/lib/schedplus/SchedPlusStandard\" \"$@\"\n",
    )

    desktop = (METADATA / f"{APPLICATION_ID}.desktop").read_text(encoding="utf-8")
    desktop = desktop.replace("Exec=schedplus-full", "Exec=SchedPlus")
    (appdir / f"{APPLICATION_ID}.desktop").write_text(desktop, encoding="utf-8")
    icon = PROJECT_ROOT / "assets" / "icons" / "icon-256.png"
    shutil.copy2(icon, appdir / f"{APPLICATION_ID}.png")
    shutil.copy2(icon, appdir / ".DirIcon")
    return appdir


def build(*, frozen_dir: Path, output_dir: Path, version: str, appimagetool: Path) -> tuple[Path, Path]:
    appdir = create_appdir(frozen_dir=frozen_dir, appdir=output_dir / "SchedPlus.AppDir")
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / f"SchedPlus-{version}-{architecture()}.AppImage"
    environment = {**os.environ, "ARCH": architecture()}
    appimagetool = appimagetool.resolve()
    subprocess.run([str(appimagetool), "--comp", "zstd", str(appdir), str(artifact)], check=True, env=environment)
    checksum = artifact.with_suffix(artifact.suffix + ".sha256")
    with artifact.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    checksum.write_text(f"{digest}  {artifact.name}\n", encoding="utf-8")
    return artifact, checksum


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--appimagetool", type=Path, required=True)
    options = parser.parse_args()
    artifact, checksum = build(**vars(options))
    print(artifact)
    print(checksum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
