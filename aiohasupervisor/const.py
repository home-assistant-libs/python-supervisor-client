"""Constants for aiohasupervisor."""

from enum import StrEnum

from aiohttp import ClientTimeout

DEFAULT_TIMEOUT = ClientTimeout(total=10)
TIMEOUT_60_SECONDS = ClientTimeout(total=60)
# Logs are streamed and following has no end, so only limit connecting
LOGS_TIMEOUT = ClientTimeout(total=None, sock_connect=10)

HEADER_HASS_SOURCE = "X-Hass-Source"

DEFAULT_UNIX_SOCKET_API_HOST = "http://localhost"


class ResponseType(StrEnum):
    """Expected response type."""

    NONE = "none"
    JSON = "json"
    STREAM = "stream"
    LINES = "lines"
    TEXT = "text"
