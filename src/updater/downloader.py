# SPDX-License-Identifier: GPL-3.0-only

"""Bounded artifact download and verification."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .errors import UpdateError, UpdateVerificationError
from .manifest import Artifact


def download_artifact(
    artifact: Artifact,
    destination: Path,
    *,
    timeout: float = 30.0,
) -> Path:
    """Download an artifact to a temporary file and promote it after verification."""
    destination = destination.resolve()
    partial = destination.with_suffix(destination.suffix + ".part")
    digest = hashlib.sha256()
    received = 0
    request = Request(artifact.url, headers={"User-Agent": "SchedPlus-Updater/1"})
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with (
            urlopen(request, timeout=timeout) as response,
            partial.open("wb") as output,
        ):
            if response.geturl().split(":", 1)[0].lower() != "https":
                raise UpdateVerificationError(
                    "The artifact download redirected to an insecure address."
                )
            while chunk := response.read(1024 * 1024):
                received += len(chunk)
                if received > artifact.size:
                    raise UpdateVerificationError(
                        "The downloaded update is larger than the signed manifest allows."
                    )
                digest.update(chunk)
                output.write(chunk)
        if received != artifact.size:
            raise UpdateVerificationError(
                "The downloaded update size does not match the signed manifest."
            )
        if digest.hexdigest() != artifact.sha256:
            raise UpdateVerificationError(
                "The downloaded update failed its SHA-256 verification."
            )
        os.replace(partial, destination)
        return destination
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise UpdateError(f"Unable to download the SchedPlus update: {exc}") from exc
    finally:
        try:
            partial.unlink(missing_ok=True)
        except OSError:
            pass
