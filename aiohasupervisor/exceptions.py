"""Exceptions from supervisor client."""


class SupervisorError(Exception):
    """Generic exception."""

    def __init__(self, message: str | None = None, job_id: str | None = None) -> None:
        """Initialize exception."""
        if message is not None:
            super().__init__(message)
        else:
            super().__init__()

        self.job_id: str | None = job_id


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


class AddonNotSupportedError(SupervisorError):
    """Addon is not supported on this system."""


class AddonNotSupportedArchitectureError(AddonNotSupportedError):
    """Addon is not supported on this system due to its architecture."""

    def __init__(
        self, addon: str, architectures: str, job_id: str | None = None
    ) -> None:
        """Initialize exception."""
        super().__init__(
            f"Add-on {addon} not supported on this platform, "
            f"supported architectures: {architectures}",
            job_id,
        )


class AddonNotSupportedMachineTypeError(AddonNotSupportedError):
    """Addon is not supported on this system due to its machine type."""

    def __init__(
        self, addon: str, machine_types: str, job_id: str | None = None
    ) -> None:
        """Initialize exception."""
        super().__init__(
            f"Add-on {addon} not supported on this machine, "
            f"supported machine types: {machine_types}",
            job_id,
        )


class AddonNotSupportedHomeAssistantVersionError(AddonNotSupportedError):
    """Addon is not supported on this system due to its version of Home Assistant."""

    def __init__(self, addon: str, version: str, job_id: str | None = None) -> None:
        """Initialize exception."""
        super().__init__(
            f"Add-on {addon} not supported on this system, "
            f"requires Home Assistant version {version} or greater",
            job_id,
        )
