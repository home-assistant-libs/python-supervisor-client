"""Exceptions from supervisor client."""

from abc import ABC
from collections.abc import Callable
from typing import Any


class SupervisorError(Exception):
    """Generic exception."""

    error_key: str | None = None

    def __init__(
        self,
        message: str | None = None,
        extra_fields: dict[str, Any] | None = None,
        job_id: str | None = None,
    ) -> None:
        """Initialize exception."""
        if message is not None:
            super().__init__(message)
        else:
            super().__init__()

        self.job_id = job_id
        self.extra_fields = extra_fields


ERROR_KEYS: dict[str, type[SupervisorError]] = {}


def error_key(
    key: str,
) -> Callable[[type[SupervisorError]], type[SupervisorError]]:
    """Store exception in keyed error map."""

    def wrap(cls: type[SupervisorError]) -> type[SupervisorError]:
        ERROR_KEYS[key] = cls
        cls.error_key = key
        return cls

    return wrap


class SupervisorConnectionError(SupervisorError, ConnectionError):
    """Unknown error connecting to supervisor."""


class SupervisorTimeoutError(SupervisorError, TimeoutError):
    """Timeout connecting to supervisor."""


class SupervisorBadRequestError(SupervisorError):
    """Invalid request made to supervisor."""


class SupervisorAuthenticationError(SupervisorError):
    """Invalid authentication sent to supervisor."""


class SupervisorForbiddenError(SupervisorError):
    """Client is not allowed to take the action requested."""


class SupervisorNotFoundError(SupervisorError):
    """Requested resource does not exist."""


class SupervisorServiceUnavailableError(SupervisorError):
    """Cannot complete request because a required service is unavailable."""


class SupervisorResponseError(SupervisorError):
    """Unusable response received from Supervisor with the wrong type or encoding."""


class AddonNotSupportedError(SupervisorError, ABC):
    """Addon is not supported on this system."""


@error_key("addon_not_supported_architecture_error")
class AddonNotSupportedArchitectureError(AddonNotSupportedError):
    """Addon is not supported on this system due to its architecture."""


@error_key("addon_not_supported_machine_type_error")
class AddonNotSupportedMachineTypeError(AddonNotSupportedError):
    """Addon is not supported on this system due to its machine type."""


@error_key("addon_not_supported_home_assistant_version_error")
class AddonNotSupportedHomeAssistantVersionError(AddonNotSupportedError):
    """Addon is not supported on this system due to its version of Home Assistant."""
