# SPDX-License-Identifier: GPL-3.0-only

"""Update discovery over a signed release feed."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import BuildInfo
from .errors import UpdateError, UpdateVerificationError
from .manifest import Artifact, parse_signed_manifest, select_artifact, version_key


@dataclass(frozen=True)
class UpdateCheckResult:
    current_version: str
    latest_version: str
    artifact: Artifact | None
    release_notes_url: str = ""

    @property
    def available(self) -> bool:
        return self.artifact is not None and version_key(
            self.latest_version
        ) > version_key(self.current_version)


def fetch_manifest(url: str, *, timeout: float = 10.0) -> bytes:
    request = Request(url, headers={"User-Agent": "SchedPlus-Updater/1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.geturl().split(":", 1)[0].lower() != "https":
                raise UpdateVerificationError(
                    "The update service redirected to an insecure address."
                )
            return response.read(2_000_001)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise UpdateError(
            f"Unable to contact the SchedPlus update service: {exc}"
        ) from exc


def check_for_update(
    info: BuildInfo, *, raw_manifest: bytes | None = None
) -> UpdateCheckResult:
    info.validate_for_updates()
    raw = (
        raw_manifest
        if raw_manifest is not None
        else fetch_manifest(info.update_manifest_url)
    )
    if len(raw) > 2_000_000:
        raise UpdateVerificationError("The update manifest exceeds the allowed size.")
    manifest = parse_signed_manifest(raw, info.update_public_key)
    if manifest.channel != info.channel:
        raise UpdateVerificationError(
            "The update manifest does not match this installation's release channel."
        )
    if version_key(info.version) < version_key(manifest.minimum_updater_version):
        raise UpdateError(
            "This release requires a newer updater. Install the latest version manually once."
        )
    artifact = select_artifact(manifest, info)
    if version_key(manifest.version) <= version_key(info.version):
        artifact = None
    return UpdateCheckResult(
        current_version=info.version,
        latest_version=manifest.version,
        artifact=artifact,
        release_notes_url=manifest.release_notes_url,
    )
