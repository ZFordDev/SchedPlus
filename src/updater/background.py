# SPDX-License-Identifier: GPL-3.0-only

"""Non-blocking automatic update preparation."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable

from .config import BuildInfo, load_build_info
from .errors import UpdateError
from .preferences import load_update_preferences
from .service import PreparedUpdate, prepare_update

LOGGER = logging.getLogger(__name__)


def start_automatic_update(
    on_ready: Callable[[BuildInfo, PreparedUpdate], None],
    on_error: Callable[[str], None] | None = None,
) -> threading.Thread | None:
    """Prepare an update on a daemon thread and report it through callbacks."""
    info = load_build_info()
    preferences = load_update_preferences()
    if not info.internally_managed or not preferences.check_automatically:
        return None

    def work() -> None:
        try:
            prepared = prepare_update(info)
        except UpdateError as exc:
            # An up-to-date result is normal; network and verification failures are
            # logged and surfaced non-modally by interfaces that provide a callback.
            if str(exc) != "SchedPlus is already up to date.":
                LOGGER.warning("Automatic update check failed: %s", exc)
                if on_error:
                    on_error(str(exc))
            return
        on_ready(info, prepared)

    thread = threading.Thread(target=work, name="schedplus-update-check", daemon=True)
    thread.start()
    return thread
