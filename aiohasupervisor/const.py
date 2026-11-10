"""Constants for aiohasupervisor."""

from enum import StrEnum

from aiohttp import ClientTimeout

DEFAULT_TIMEOUT = ClientTimeout(total=10)
TIMEOUT_60_SECONDS = ClientTimeout(total=60)
# Logs are streamed and following has no end, so only limit connecting
LOGS_CONNECT_TIMEOUT = 10
LOGS_TIMEOUT = ClientTimeout(total=None, connect=LOGS_CONNECT_TIMEOUT)

HEADER_HASS_SOURCE = "X-Hass-Source"

DEFAULT_UNIX_SOCKET_API_HOST = "http://localhost"

# Characters yarl leaves unencoded in a path segment (RFC 3986 sub-delims, ":"
# and "@"). Quoting them would be undone when the URL is built, so a free-form
# value put in a path must leave exactly these safe.
PATH_SEGMENT_SAFE = "!$&'()*,:;=@"


class ResponseType(StrEnum):
    """Expected response type."""

    NONE = "none"
    JSON = "json"
    STREAM = "stream"
    LINES = "lines"
    TEXT = "text"
