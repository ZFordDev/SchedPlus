"""Build and validate the SchedPlus Standard MSIX package."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

import tomllib

try:
    from scripts.update_release_metadata import embed_packaged_build_info
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from update_release_metadata import embed_packaged_build_info


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MSIX_DIRECTORY = PROJECT_ROOT / "packaging" / "msix"
ASSET_SIZES = {
    "Square44x44Logo.png": (44, 44),
    "Square71x71Logo.png": (71, 71),
    "Square150x150Logo.png": (150, 150),
    "Square310x310Logo.png": (310, 310),
    "StoreLogo.png": (50, 50),
    "Wide310x150Logo.png": (310, 150),
}


def package_version() -> str:
    """Return pyproject's release version in the four-part MSIX form."""
    project = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    parts = project["project"]["version"].split(".")
    if len(parts) > 4 or not all(part.isdigit() for part in parts):
        raise ValueError("project version must be a numeric MSIX-compatible version")
    return ".".join([*parts, *("0" for _ in range(4 - len(parts)))])


def render_manifest(*, identity_name: str, publisher: str, publisher_display_name: str) -> str:
    """Render the Store-owned identity into the committed manifest template."""
    values = {
        "IDENTITY_NAME": identity_name,
        "PUBLISHER": publisher,
        "PUBLISHER_DISPLAY_NAME": publisher_display_name,
        "VERSION": package_version(),
    }
    if not all(value.strip() for value in values.values()):
        raise ValueError("Partner Center identity name and publisher values are required")
    if any("{{" in value or "}}" in value for value in values.values()):
        raise ValueError("identity values must not contain manifest template markers")

    manifest = (MSIX_DIRECTORY / "AppxManifest.xml.template").read_text(encoding="utf-8")
    for key, value in values.items():
        manifest = manifest.replace(f"{{{{{key}}}}}", escape(value, {'"': "&quot;"}))
    if "{{" in manifest or "}}" in manifest:
        raise RuntimeError("manifest contains unresolved template markers")
    return manifest


def create_visual_assets(destination: Path) -> None:
    """Create required Store logos from the committed 512px application icon."""
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required to generate MSIX visual assets") from exc

    source = Image.open(PROJECT_ROOT / "assets" / "icons" / "icon-512.png").convert("RGBA")
    destination.mkdir(parents=True, exist_ok=True)
    for filename, size in ASSET_SIZES.items():
        if size[0] == size[1]:
            image = source.resize(size, Image.Resampling.LANCZOS)
        else:
            icon_size = min(size)
            icon = source.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            image = Image.new("RGBA", size, (0, 0, 0, 0))
            image.paste(icon, ((size[0] - icon_size) // 2, 0), icon)
        image.save(destination / filename)


def stage_package(
    *,
    frozen_dir: Path,
    stage: Path,
    identity_name: str,
    publisher: str,
    publisher_display_name: str,
) -> None:
    """Copy the frozen Standard payload and MSIX metadata into a clean stage."""
    if frozen_dir.name != "SchedPlusStandard" or not (frozen_dir / "SchedPlusStandard.exe").is_file():
        raise ValueError("--frozen-dir must be a SchedPlusStandard PyInstaller onedir directory")
    shutil.copytree(frozen_dir, stage, dirs_exist_ok=True)
    embed_packaged_build_info(
        stage,
        version=package_version().removesuffix(".0"),
        edition="standard",
        platform="win32",
        architecture="x86_64",
        package_format="msix-store",
        externally_managed=True,
    )
    (stage / "AppxManifest.xml").write_text(
        render_manifest(
            identity_name=identity_name,
            publisher=publisher,
            publisher_display_name=publisher_display_name,
        ),
        encoding="utf-8",
    )
    create_visual_assets(stage / "Assets")
    shutil.copy2(MSIX_DIRECTORY / "SOURCE.txt", stage / "SOURCE.txt")


def build(
    *,
    frozen_dir: Path,
    output_dir: Path,
    identity_name: str,
    publisher: str,
    publisher_display_name: str,
    makeappx: Path,
) -> Path:
    """Create an unsigned MSIX and validate its package structure."""
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / f"SchedPlus_{package_version()}_x64.msix"
    if artifact.exists():
        artifact.unlink()
    command = str(makeappx.resolve())
    with tempfile.TemporaryDirectory(prefix="schedplus-msix-") as temporary:
        stage = Path(temporary) / "SchedPlus"
        stage_package(
            frozen_dir=frozen_dir,
            stage=stage,
            identity_name=identity_name,
            publisher=publisher,
            publisher_display_name=publisher_display_name,
        )
        subprocess.run([command, "pack", "/d", str(stage), "/p", str(artifact), "/o"], check=True)
        verification = Path(temporary) / "verification"
        subprocess.run([command, "unpack", "/p", str(artifact), "/d", str(verification), "/o"], check=True)
        if not (verification / "AppxManifest.xml").is_file():
            raise RuntimeError("MakeAppx could not unpack a complete MSIX manifest")
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--identity-name", required=True)
    parser.add_argument("--publisher", required=True)
    parser.add_argument("--publisher-display-name", required=True)
    parser.add_argument("--makeappx", type=Path, required=True)
    options = parser.parse_args()
    print(build(**vars(options)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
