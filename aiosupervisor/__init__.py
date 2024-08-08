"""Init file for aiosupervisor."""

from aiosupervisor.exceptions import (
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
from aiosupervisor.root import SupervisorClient

__all__ = [
    "SupervisorError",
    "SupervisorConnectionError",
    "SupervisorAuthenticationError",
    "SupervisorBadRequestError",
    "SupervisorForbiddenError",
    "SupervisorNotFoundError",
    "SupervisorResponseError",
    "SupervisorServiceUnavailableError",
    "SupervisorTimeoutError",
    "SupervisorClient",
]
