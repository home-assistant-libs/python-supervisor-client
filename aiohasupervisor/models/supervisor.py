"""Models for supervisor component."""

from dataclasses import dataclass

from .base import Options, Request, ResponseData
from .root import LogLevel, UpdateChannel


@dataclass(frozen=True, slots=True)
class SupervisorInfo(ResponseData):
    """SupervisorInfo model."""

    version: str
    version_latest: str
    update_available: bool
    channel: UpdateChannel
    arch: str
    supported: bool
    healthy: bool
    ip_address: str
    timezone: str | None
    logging: LogLevel
    debug: bool
    debug_block: bool
    diagnostics: bool | None
    auto_update: bool


@dataclass(frozen=True, slots=True)
class SupervisorStats(ResponseData):
    """SupervisorStats model."""

    cpu_percent: float
    memory_usage: int
    memory_limit: int
    memory_percent: float
    network_rx: int
    network_tx: int
    blk_read: int
    blk_write: int


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