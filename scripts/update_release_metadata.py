"""Create package build identity and signed update manifests."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
from pathlib import Path

FORMATS = {
    ".AppImage": ("standard", "linux", "appimage"),
    ".deb": (None, "linux", "deb"),
    ".exe": ("standard", "win32", "windows-installer"),
    ".zip": (None, "win32", "managed-zip"),
}
EDITION_NAMES = {
    "Standard": "standard",
    "Lite": "lite",
    "Full": "full",
    "CLI": "cli",
    "schedplus": "standard",
    "schedplus-lite": "lite",
    "schedplus-cli": "cli",
}


def build_info_document(
    *,
    version: str,
    edition: str,
    platform: str,
    architecture: str,
    package_format: str,
    channel: str,
    manifest_url: str,
    public_key: str,
    updates_enabled: bool,
    updater_executable: str = "",
    install_root: str = "",
    launch_relative_path: str = "",
) -> dict:
    """Return validated metadata suitable for ``schedplus/build-info.json``."""
    if edition not in {"standard", "lite", "full", "cli"}:
        raise ValueError(f"invalid edition: {edition}")
    if channel not in {"stable", "preview"}:
        raise ValueError(f"invalid channel: {channel}")
    if updates_enabled:
        if not manifest_url.startswith("https://"):
            raise ValueError("enabled updates require an HTTPS manifest URL")
        key = base64.b64decode(public_key, validate=True)
        if len(key) != 32:
            raise ValueError("update public key must be a base64 Ed25519 public key")
    return {
        "version": version,
        "edition": edition,
        "platform": platform,
        "architecture": architecture,
        "format": package_format,
        "channel": channel,
        "update_manifest_url": manifest_url,
        "update_public_key": public_key,
        "updates_enabled": updates_enabled,
        "updater_executable": updater_executable,
        "install_root": install_root,
        "launch_relative_path": launch_relative_path,
    }


def write_build_info(destination: Path, **values) -> Path:
    document = build_info_document(**values)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return destination


def embedded_build_info_path(payload: Path) -> Path:
    """Locate the package resource directory inside a PyInstaller onedir tree."""
    internal = payload / "_internal" / "schedplus"
    return internal / "build-info.json"


def embed_packaged_build_info(
    payload: Path,
    *,
    version: str,
    edition: str,
    platform: str,
    architecture: str,
    package_format: str,
    externally_managed: bool = False,
    updates_supported: bool = True,
    updater_executable: str = "",
    install_root: str = "",
    launch_relative_path: str = "",
) -> Path:
    """Embed policy supplied by the packaging/release environment."""
    enabled = (
        os.environ.get("SCHEDPLUS_ENABLE_UPDATES") == "1"
        and updates_supported
        and not externally_managed
    )
    channel = os.environ.get("SCHEDPLUS_UPDATE_CHANNEL", "stable")
    manifest_url = os.environ.get(
        "SCHEDPLUS_UPDATE_MANIFEST_URL",
        f"https://github.com/ZFordDev/SchedPlus/releases/latest/download/{channel}.json",
    )
    public_key = os.environ.get("SCHEDPLUS_UPDATE_PUBLIC_KEY", "")
    return write_build_info(
        embedded_build_info_path(payload),
        version=version,
        edition=edition,
        platform=platform,
        architecture=architecture,
        package_format=package_format,
        channel=channel,
        manifest_url=manifest_url,
        public_key=public_key,
        updates_enabled=enabled,
        updater_executable=updater_executable,
        install_root=install_root,
        launch_relative_path=launch_relative_path,
    )


def _artifact_identity(path: Path) -> tuple[str, str, str, str]:
    suffix = next((item for item in FORMATS if path.name.endswith(item)), None)
    if suffix is None:
        raise ValueError(f"unsupported update artifact: {path.name}")
    default_edition, platform, package_format = FORMATS[suffix]
    architecture = "x86_64"
    if suffix == ".deb":
        name, _, architecture = path.name.partition("_")
        edition = EDITION_NAMES.get(name)
    elif suffix == ".zip":
        match = re.match(r"SchedPlus-(Standard|Lite|Full|CLI)-", path.name)
        edition = EDITION_NAMES.get(match.group(1)) if match else None
    else:
        edition = default_edition
    if not edition:
        raise ValueError(f"cannot determine artifact edition: {path.name}")
    return edition, platform, architecture, package_format


def generate_signed_manifest(
    *,
    artifact_directory: Path,
    output: Path,
    version: str,
    channel: str,
    minimum_updater_version: str,
    release_base_url: str,
    release_notes_url: str,
    private_key_b64: str,
) -> Path:
    """Generate a signed manifest without writing or logging private material."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    from updater.manifest import canonical_payload

    private_bytes = base64.b64decode(private_key_b64, validate=True)
    if len(private_bytes) != 32:
        raise ValueError("signing key must be a base64 Ed25519 private key")
    artifacts = []
    for path in sorted(artifact_directory.iterdir()):
        if not path.is_file() or not any(path.name.endswith(item) for item in FORMATS):
            continue
        edition, platform, architecture, package_format = _artifact_identity(path)
        artifacts.append(
            {
                "edition": edition,
                "platform": platform,
                "architecture": architecture,
                "format": package_format,
                "url": f"{release_base_url.rstrip('/')}/{path.name}",
                "size": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    if not artifacts:
        raise ValueError("no supported update artifacts were found")
    document = {
        "version": version,
        "channel": channel,
        "minimum_updater_version": minimum_updater_version,
        "release_notes_url": release_notes_url,
        "artifacts": artifacts,
    }
    signature = Ed25519PrivateKey.from_private_bytes(private_bytes).sign(
        canonical_payload(document)
    )
    document["signature"] = base64.b64encode(signature).decode("ascii")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    identity = subparsers.add_parser("build-info")
    identity.add_argument("--destination", type=Path, required=True)
    identity.add_argument("--version", required=True)
    identity.add_argument("--edition", choices=("standard", "lite", "full", "cli"), required=True)
    identity.add_argument("--platform", required=True)
    identity.add_argument("--architecture", required=True)
    identity.add_argument("--format", dest="package_format", required=True)
    identity.add_argument("--channel", choices=("stable", "preview"), default="stable")
    identity.add_argument("--manifest-url", default="")
    identity.add_argument("--public-key", default="")
    identity.add_argument("--updates-enabled", action="store_true")
    manifest = subparsers.add_parser("manifest")
    manifest.add_argument("--artifact-directory", type=Path, required=True)
    manifest.add_argument("--output", type=Path, required=True)
    manifest.add_argument("--version", required=True)
    manifest.add_argument("--channel", choices=("stable", "preview"), required=True)
    manifest.add_argument("--minimum-updater-version", default="0.8.1")
    manifest.add_argument("--release-base-url", required=True)
    manifest.add_argument("--release-notes-url", required=True)
    options = parser.parse_args()
    if options.command == "build-info":
        values = vars(options)
        values.pop("command")
        print(write_build_info(**values))
    elif options.command == "manifest":
        values = vars(options)
        values.pop("command")
        values["private_key_b64"] = os.environ["SCHEDPLUS_UPDATE_SIGNING_KEY"]
        print(generate_signed_manifest(**values))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
