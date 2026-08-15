# SPDX-License-Identifier: GPL-3.0-only

"""Build-time identity and update policy."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from importlib import metadata, resources
from pathlib import Path

from .errors import UpdateConfigurationError

STORE_FORMATS = {"snap", "msix-store", "microsoft-store"}
EDITIONS = {"standard", "lite", "full", "cli"}
CHANNELS = {"stable", "preview"}


@dataclass(frozen=True)
class BuildInfo:
    version: str
    edition: str = "full"
    package_format: str = "source"
    platform: str = sys.platform
    architecture: str = "unknown"
    channel: str = "stable"
    update_manifest_url: str = ""
    update_public_key: str = ""
    updater_executable: str = ""
    install_root: str = ""
    launch_relative_path: str = ""
    updates_enabled: bool = False

    @property
    def internally_managed(self) -> bool:
        return self.package_format not in STORE_FORMATS and self.updates_enabled

    def validate_for_updates(self) -> None:
        if not self.internally_managed:
            raise UpdateConfigurationError(
                "Updates for this installation are managed externally or are disabled."
            )
        if self.edition not in EDITIONS:
            raise UpdateConfigurationError(f"Unknown SchedPlus edition: {self.edition}")
        if self.channel not in CHANNELS:
            raise UpdateConfigurationError(f"Unknown update channel: {self.channel}")
        if not self.update_manifest_url.startswith("https://"):
            raise UpdateConfigurationError(
                "This build does not provide a secure update manifest URL."
            )
        if not self.update_public_key:
            raise UpdateConfigurationError(
                "This build does not provide an update verification key."
            )


def _installed_version() -> str:
    try:
        return metadata.version("schedplus")
    except metadata.PackageNotFoundError:
        return "0.0.0"


def _embedded_build_info() -> dict:
    try:
        resource = resources.files("schedplus").joinpath("build-info.json")
        if resource.is_file():
            return json.loads(resource.read_text(encoding="utf-8"))
    except (
        FileNotFoundError,
        ModuleNotFoundError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):
        pass
    return {}


def load_build_info() -> BuildInfo:
    """Load immutable identity embedded by packaging, with safe source defaults."""
    values = _embedded_build_info()
    architecture = values.get("architecture") or os.environ.get(
        "SCHEDPLUS_BUILD_ARCH", "unknown"
    )
    info = BuildInfo(
        version=str(values.get("version") or _installed_version()),
        edition=str(values.get("edition", "full")),
        package_format=str(values.get("format", values.get("package_format", "source"))),
        platform=str(values.get("platform", sys.platform)),
        architecture=str(architecture),
        channel=str(values.get("channel", "stable")),
        update_manifest_url=str(values.get("update_manifest_url", "")),
        update_public_key=str(values.get("update_public_key", "")),
        updater_executable=str(values.get("updater_executable", "")),
        install_root=str(values.get("install_root", "")),
        launch_relative_path=str(values.get("launch_relative_path", "")),
        updates_enabled=bool(values.get("updates_enabled", False)),
    )
    if info.package_format in STORE_FORMATS and info.updates_enabled:
        return BuildInfo(**{**info.__dict__, "updates_enabled": False})
    return info


def resolve_install_root(info: BuildInfo) -> Path:
    if not info.install_root:
        raise UpdateConfigurationError(
            "This build does not define its installation root."
        )
    configured = Path(info.install_root).expanduser()
    if configured.is_absolute():
        return configured.resolve()
    return (Path(sys.executable).resolve().parent / configured).resolve()


def resolve_updater_executable(info: BuildInfo) -> Path:
    if not info.updater_executable:
        raise UpdateConfigurationError(
            "This build does not define an external updater."
        )
    configured = Path(info.updater_executable).expanduser()
    if configured.is_absolute():
        return configured.resolve()
    return (Path(sys.executable).resolve().parent / configured).resolve()
