"""Prepare legacy data, verify upgrades, and sanitize smoke-test logs."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sqlite3
import urllib.request
from pathlib import Path

SMOKE_TASK_ID = "00000000-0000-0000-0000-000000000081"
SMOKE_TASK_TEXT = "SchedPlus release smoke test"
SECRET_PATTERN = re.compile(
    r"(?i)(password|private[_ -]?key|secret|token|credential)(\s*[:=]\s*)(\S+)"
)


def seed_legacy_database(path: Path, release: str) -> None:
    """Create the populated schema shipped by 0.7.3 and 0.8.0."""
    if release not in {"0.7.3", "0.8.0"}:
        raise ValueError(f"unsupported legacy release: {release}")
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE entries (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                text TEXT NOT NULL,
                createdAt TEXT NOT NULL,
                updatedAt TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?)",
            (
                SMOKE_TASK_ID,
                "2026-08-15",
                "09:30",
                SMOKE_TASK_TEXT,
                "2026-08-15T00:00:00+00:00",
                "2026-08-15T00:00:00+00:00",
            ),
        )


def verify_upgraded_database(path: Path, expected_schema: int) -> None:
    if not path.is_file():
        raise ValueError(f"database was not created: {path}")
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
        version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        row = connection.execute(
            "SELECT text FROM entries WHERE id = ?", (SMOKE_TASK_ID,)
        ).fetchone()
    if version != expected_schema:
        raise ValueError(f"expected schema {expected_schema}, found {version}")
    if row != (SMOKE_TASK_TEXT,):
        raise ValueError("the populated previous-version task was not preserved")


def sanitize_log(source: Path, output: Path, replacements: list[str]) -> None:
    text = (
        source.read_text(encoding="utf-8", errors="replace")
        if source.exists()
        else "No application log was created.\n"
    )
    for value in sorted((item for item in replacements if item), key=len, reverse=True):
        text = text.replace(value, "<redacted-path>")
    text = SECRET_PATTERN.sub(r"\1\2<redacted>", text)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")


def download_release_asset(
    *,
    repository: str,
    token: str,
    tag: str,
    pattern: str,
    directory: Path,
) -> Path:
    """Download one asset from a published or draft release."""
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "SchedPlus-post-release-smoke",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/releases?per_page=100",
        headers=headers,
    )
    with urllib.request.urlopen(request) as response:
        releases = json.load(response)
    release = next((item for item in releases if item.get("tag_name") == tag), None)
    if release is None:
        raise ValueError(f"release not found: {tag}")
    matches = [
        asset
        for asset in release.get("assets", [])
        if fnmatch.fnmatchcase(asset.get("name", ""), pattern)
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected one asset matching {pattern!r}, found {len(matches)}"
        )
    asset = matches[0]
    asset_headers = {**headers, "Accept": "application/octet-stream"}
    asset_request = urllib.request.Request(asset["url"], headers=asset_headers)
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / asset["name"]
    with urllib.request.urlopen(asset_request) as response:
        destination.write_bytes(response.read())
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    seed = commands.add_parser("seed")
    seed.add_argument("--database", type=Path, required=True)
    seed.add_argument("--release", choices=("0.7.3", "0.8.0"), default="0.8.0")
    verify = commands.add_parser("verify")
    verify.add_argument("--database", type=Path, required=True)
    verify.add_argument("--schema", type=int, required=True)
    sanitize = commands.add_parser("sanitize")
    sanitize.add_argument("--source", type=Path, required=True)
    sanitize.add_argument("--output", type=Path, required=True)
    sanitize.add_argument("--redact", action="append", default=[])
    download = commands.add_parser("download")
    download.add_argument("--tag", required=True)
    download.add_argument("--pattern", required=True)
    download.add_argument("--directory", type=Path, required=True)
    options = parser.parse_args()
    if options.command == "seed":
        seed_legacy_database(options.database, options.release)
    elif options.command == "verify":
        verify_upgraded_database(options.database, options.schema)
    elif options.command == "sanitize":
        sanitize_log(options.source, options.output, options.redact)
    else:
        download_release_asset(
            repository=os.environ["GITHUB_REPOSITORY"],
            token=os.environ["GITHUB_TOKEN"],
            tag=options.tag,
            pattern=options.pattern,
            directory=options.directory,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
