# SPDX-License-Identifier: GPL-3.0-only

"""Secure, package-aware update support for SchedPlus."""

from .checker import UpdateCheckResult, check_for_update
from .config import BuildInfo, load_build_info
from .errors import UpdateError

__all__ = [
    "BuildInfo",
    "UpdateCheckResult",
    "UpdateError",
    "check_for_update",
    "load_build_info",
]
