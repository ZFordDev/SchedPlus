# SPDX-License-Identifier: GPL-3.0-only

"""Signed update-manifest parsing and artifact selection."""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .config import BuildInfo
from .errors import UpdateVerificationError

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VERSION_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+]([0-9A-Za-z.-]+))?$"
)


@dataclass(frozen=True)
class Artifact:
    edition: str
    platform: str
    architecture: str
    package_format: str
    url: str
    size: int
    sha256: str


@dataclass(frozen=True)
class UpdateManifest:
    version: str
    channel: str
    minimum_updater_version: str
    release_notes_url: str
    artifacts: tuple[Artifact, ...]


def canonical_payload(document: dict[str, Any]) -> bytes:
    unsigned = {key: value for key, value in document.items() if key != "signature"}
    return json.dumps(
        unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def parse_signed_manifest(raw: bytes, public_key_b64: str) -> UpdateManifest:
    try:
        document = json.loads(raw.decode("utf-8"))
        signature = base64.b64decode(document["signature"], validate=True)
        public_key = base64.b64decode(public_key_b64, validate=True)
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            signature, canonical_payload(document)
        )
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        raise UpdateVerificationError(
            "The update manifest is malformed or incomplete."
        ) from None
    except InvalidSignature:
        raise UpdateVerificationError(
            "The update manifest signature could not be verified."
        ) from None

    try:
        artifacts = tuple(_parse_artifact(item) for item in document["artifacts"])
        manifest = UpdateManifest(
            version=_version(document["version"]),
            channel=str(document["channel"]),
            minimum_updater_version=_version(document["minimum_updater_version"]),
            release_notes_url=str(document.get("release_notes_url", "")),
            artifacts=artifacts,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise UpdateVerificationError(f"Invalid update manifest: {exc}") from None

    if manifest.channel not in {"stable", "preview"}:
        raise UpdateVerificationError("The update manifest has an unknown channel.")
    return manifest


def _version(value: object) -> str:
    text = str(value)
    if not VERSION_RE.fullmatch(text):
        raise ValueError(f"invalid semantic version {text!r}")
    return text


def version_key(value: str) -> tuple[int, int, int, int, str]:
    match = VERSION_RE.fullmatch(value)
    if not match:
        raise ValueError(f"invalid semantic version {value!r}")
    major, minor, patch, suffix = match.groups()
    return int(major), int(minor), int(patch), 1 if suffix is None else 0, suffix or ""


def _parse_artifact(item: object) -> Artifact:
    if not isinstance(item, dict):
        raise TypeError("artifact entries must be objects")
    sha256 = str(item["sha256"]).lower()
    url = str(item["url"])
    size = int(item["size"])
    if not SHA256_RE.fullmatch(sha256):
        raise ValueError("artifact SHA-256 is invalid")
    if not url.startswith("https://"):
        raise ValueError("artifact URL must use HTTPS")
    if size <= 0:
        raise ValueError("artifact size must be positive")
    return Artifact(
        edition=str(item["edition"]),
        platform=str(item["platform"]),
        architecture=str(item["architecture"]),
        package_format=str(item["format"]),
        url=url,
        size=size,
        sha256=sha256,
    )


def select_artifact(manifest: UpdateManifest, info: BuildInfo) -> Artifact | None:
    matches = [
        artifact
        for artifact in manifest.artifacts
        if artifact.edition == info.edition
        and artifact.platform == info.platform
        and artifact.architecture == info.architecture
        and artifact.package_format == info.package_format
    ]
    if len(matches) > 1:
        raise UpdateVerificationError(
            "The update manifest contains duplicate artifacts for this installation."
        )
    return matches[0] if matches else None
