"""Shared application identity for every SchedPlus interface."""

from __future__ import annotations

from dataclasses import dataclass

from updater.config import BuildInfo, load_build_info


@dataclass(frozen=True)
class ApplicationIdentity:
    """User-facing identity derived from immutable package build metadata."""

    version: str
    edition: str
    channel: str
    package_format: str
    platform: str
    architecture: str

    @property
    def version_label(self) -> str:
        return f"SchedPlus v{self.version}"

    @property
    def details(self) -> str:
        return "\n".join(
            (
                self.version_label,
                f"Edition: {self.edition.title()}",
                f"Update channel: {self.channel.title()}",
                f"Package: {self.package_format}",
                f"Platform: {self.platform} ({self.architecture})",
            )
        )


def get_application_identity(
    build_info: BuildInfo | None = None,
) -> ApplicationIdentity:
    """Return the common identity, using packaged metadata when available."""
    info = build_info or load_build_info()
    return ApplicationIdentity(
        version=info.version,
        edition=info.edition,
        channel=info.channel,
        package_format=info.package_format,
        platform=info.platform,
        architecture=info.architecture,
    )
