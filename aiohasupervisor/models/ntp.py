"""Models for NTP APIs."""

from dataclasses import dataclass

from .base import Options, ResponseData

# --- OBJECTS ----


@dataclass(frozen=True, slots=True)
class NTPInfo(ResponseData):
    """NTPInfo model."""

    servers: list[str]
    fallback_servers: list[str]


@dataclass(frozen=True, slots=True)
class NTPOptions(Options):
    """NTPOptions model.

    An empty list clears the servers and returns to the OS defaults.
    """

    servers: list[str] | None = None
    fallback_servers: list[str] | None = None
