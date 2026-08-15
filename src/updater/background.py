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
from .state import UpdateState, write_state

LOGGER = logging.getLogger(__name__)


def _record_state(state: UpdateState) -> None:
    try:
        write_state(state)
    except UpdateError as exc:
        LOGGER.warning("Unable to record update result: %s", exc)


def start_automatic_update(
    on_ready: Callable[[BuildInfo, PreparedUpdate], None],
    on_error: Callable[[str], None] | None = None,
) -> threading.Thread | None:
    """Prepare an update on a daemon thread and report it through callbacks."""
    if not load_update_preferences().check_automatically:
        return None
    return start_update_check(on_ready, on_error)


def start_update_check(
    on_ready: Callable[[BuildInfo, PreparedUpdate], None],
    on_error: Callable[[str], None] | None = None,
) -> threading.Thread | None:
    """Run a user-requested update check without blocking an interface."""
    info = load_build_info()
    if not info.internally_managed:
        if on_error:
            on_error("Updates are managed externally or disabled for this build.")
        return None

    def work() -> None:
        _record_state(UpdateState("checking", current_version=info.version))
        try:
            prepared = prepare_update(info)
        except UpdateError as exc:
            # An up-to-date result is normal; network and verification failures are
            # logged and surfaced non-modally by interfaces that provide a callback.
            if str(exc) != "SchedPlus is already up to date.":
                _record_state(
                    UpdateState("failed", current_version=info.version, message=str(exc))
                )
                LOGGER.warning("Automatic update check failed: %s", exc)
                if on_error:
                    on_error(str(exc))
            else:
                _record_state(
                    UpdateState(
                        "up_to_date",
                        current_version=info.version,
                        target_version=info.version,
                        message="No newer compatible release was found.",
                    )
                )
            return
        _record_state(
            UpdateState(
                "ready",
                current_version=info.version,
                target_version=prepared.check.latest_version,
                message="A verified update is ready.",
            )
        )
        on_ready(info, prepared)

    thread = threading.Thread(target=work, name="schedplus-update-check", daemon=True)
    thread.start()
    return thread
