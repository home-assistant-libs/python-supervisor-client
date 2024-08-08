"""Constants for aiosupervisor."""

from enum import StrEnum


class ResponseType(StrEnum):
    """Expected response type."""

    NONE = "none"
    JSON = "json"
    TEXT = "text"
