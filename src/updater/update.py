# SPDX-License-Identifier: GPL-3.0-only

"""Independent updater executable entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import UpdateError
from .installer import apply_managed_update, rollback_managed_update


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="schedplus-updater")
    commands = parser.add_subparsers(dest="command", required=True)
    apply_parser = commands.add_parser("apply-managed")
    apply_parser.add_argument("--root", type=Path, required=True)
    apply_parser.add_argument("--staged", type=Path, required=True)
    apply_parser.add_argument("--launch", required=True)
    apply_parser.add_argument("--pid", type=int, default=0)
    apply_parser.add_argument("--current-version", default="")
    apply_parser.add_argument("--target-version", default="")

    rollback_parser = commands.add_parser("rollback-managed")
    rollback_parser.add_argument("--root", type=Path, required=True)
    return parser


def main(arguments: list[str] | None = None) -> int:
    options = build_parser().parse_args(arguments)
    try:
        if options.command == "apply-managed":
            apply_managed_update(
                options.root,
                options.staged,
                options.launch,
                original_pid=options.pid,
                current_version=options.current_version,
                target_version=options.target_version,
            )
        else:
            rollback_managed_update(options.root)
        return 0
    except UpdateError as exc:
        print(f"SchedPlus update failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
