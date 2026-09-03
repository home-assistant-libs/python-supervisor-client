"""Models for time APIs."""

from dataclasses import dataclass

from .base import Options, ResponseData

# --- OBJECTS ----


@dataclass(frozen=True, slots=True)
class TimeConfig(ResponseData):
    """TimeConfig model."""

    servers: list[str]
    fallback_servers: list[str]


@dataclass(frozen=True, slots=True)
class TimeInfo(ResponseData):
    """TimeInfo model."""

    config: TimeConfig


@dataclass(frozen=True, slots=True)
class TimeOptions(Options):
    """TimeOptions model.

    An empty list clears the servers and returns to the OS defaults.
    """

    servers: list[str] | None = None
    fallback_servers: list[str] | None = None
