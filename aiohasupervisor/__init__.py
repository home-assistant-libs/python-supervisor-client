"""Init file for aiohasupervisor."""

from aiohasupervisor.exceptions import (
    AddonNotSupportedArchitectureError,
    AddonNotSupportedError,
    AddonNotSupportedHomeAssistantVersionError,
    AddonNotSupportedMachineTypeError,
    SupervisorAuthenticationError,
    SupervisorBadRequestError,
    SupervisorConnectionError,
    SupervisorError,
    SupervisorForbiddenError,
    SupervisorNotFoundError,
    SupervisorResponseError,
    SupervisorServiceUnavailableError,
    SupervisorTimeoutError,
)
from aiohasupervisor.root import SupervisorClient

__all__ = [
    "AddonNotSupportedArchitectureError",
    "AddonNotSupportedError",
    "AddonNotSupportedHomeAssistantVersionError",
    "AddonNotSupportedMachineTypeError",
    "SupervisorAuthenticationError",
    "SupervisorBadRequestError",
    "SupervisorClient",
    "SupervisorConnectionError",
    "SupervisorError",
    "SupervisorForbiddenError",
    "SupervisorNotFoundError",
    "SupervisorResponseError",
    "SupervisorServiceUnavailableError",
    "SupervisorTimeoutError",
]
