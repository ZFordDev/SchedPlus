# SPDX-License-Identifier: GPL-3.0-only

"""User-presentable updater failures."""


class UpdateError(RuntimeError):
    """An update failure that can be reported at an application boundary."""


class UpdateConfigurationError(UpdateError):
    """The installed build does not have valid updater metadata."""


class UpdateVerificationError(UpdateError):
    """Downloaded metadata or content failed authenticity checks."""


class UpdateInstallError(UpdateError):
    """A staged release could not be installed or rolled back safely."""
