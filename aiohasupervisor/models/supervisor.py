"""Models for supervisor component."""

from dataclasses import dataclass
from enum import StrEnum
from ipaddress import IPv4Address

from .base import ContainerStats, Options, Request, ResponseData
from .root import LogLevel, UpdateChannel

# --- ENUMS ----


class DetectBlockingIO(StrEnum):
    """DetectBlockingIO type."""

    OFF = "off"
    ON = "on"
    ON_AT_STARTUP = "on_at_startup"


class FeatureFlag(StrEnum):
    """FeatureFlag type.

    This is an incomplete list. Supervisor regularly adds new feature flags as
    new development features are introduced. Therefore when returning feature flags,
    some keys may not be in this list and will be parsed as strings on older versions
    of the client.
    """

    SUPERVISOR_V2_API = "supervisor_v2_api"
    UNIX_SOCKET_CORE_API = "unix_socket_core_api"


# --- OBJECTS ----


@dataclass(frozen=True, slots=True)
class SupervisorInfo(ResponseData):
    """SupervisorInfo model."""

    version: str
    version_latest: str | None
    update_available: bool
    channel: UpdateChannel
    arch: str | None
    supported: bool
    healthy: bool
    ip_address: IPv4Address
    timezone: str | None
    logging: LogLevel
    debug: bool
    debug_block: bool
    diagnostics: bool | None
    auto_update: bool
    country: str | None
    detect_blocking_io: bool
    feature_flags: dict[FeatureFlag | str, bool]


@dataclass(frozen=True, slots=True)
class SupervisorStats(ContainerStats):
    """SupervisorStats model."""


@dataclass(frozen=True, slots=True)
class SupervisorUpdateOptions(Request):
    """SupervisorUpdateOptions model."""

    version: str


@dataclass(frozen=True, slots=True)
class SupervisorOptions(Options):
    """SupervisorOptions model."""

    channel: UpdateChannel | None = None
    timezone: str | None = None
    logging: LogLevel | None = None
    debug: bool | None = None
    debug_block: bool | None = None
    diagnostics: bool | None = None
    content_trust: bool | None = None
    force_security: bool | None = None
    auto_update: bool | None = None
    country: str | None = None
    detect_blocking_io: DetectBlockingIO | None = None
    feature_flags: dict[FeatureFlag, bool] | None = None
