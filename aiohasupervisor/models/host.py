"""Models for host APIs."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from .base import Request, ResponseData
from .root import HostFeature

# --- ENUMS ----


class ServiceState(StrEnum):
    """ServiceState type.

    The service state is determined by systemd, not supervisor. The list below
    is pulled from `systemctl --state=help`. It may be incomplete and it may
    change based on the host. Therefore within a list of services there may be
    some with a state not in this list parsed as string. If you find this
    please create an issue or pr to get the state added.
    """

    ACTIVE = "active"
    RELOADING = "reloading"
    INACTIVE = "inactive"
    FAILED = "failed"
    ACTIVATING = "activating"
    DEACTIVATING = "deactivating"
    MAINTENANCE = "maintenance"


class LogFormat(StrEnum):
    """LogFormat type.

    Format of each line of a log read from the journal. Plain is the message only,
    timestamp adds the time and verbose also adds the host and process.

    This is an incomplete list. Supervisor may add new log formats. Therefore when
    returning the log format of apps, some may have a log format that is not in this
    list parsed as strings on older versions of the client.
    """

    PLAIN = "plain"
    TIMESTAMP = "timestamp"
    VERBOSE = "verbose"


# --- OBJECTS ----


@dataclass(frozen=True, slots=True)
class HostInfo(ResponseData):
    """HostInfo model."""

    agent_version: str | None
    apparmor_version: str | None
    chassis: str | None
    virtualization: str | None
    cpe: str | None
    deployment: str | None
    disk_free: float
    disk_total: float
    disk_used: float
    disk_life_time: float | None
    features: list[HostFeature | str]
    hostname: str | None
    llmnr_hostname: str | None
    kernel: str | None
    operating_system: str | None
    timezone: str | None
    dt_utc: datetime | None
    dt_synchronized: bool | None
    use_ntp: bool | None
    startup_time: float | None
    boot_timestamp: int | None
    broadcast_llmnr: bool | None
    broadcast_mdns: bool | None

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Prefer all_features over features field if present.

        Supervisor sends the full, unfiltered list of features as all_features
        while features may omit some for backwards compatibility with older
        clients. Only merge it into features here (rather than aliasing the
        field to all_features) so that a to_dict/from_dict round trip of this
        model continues to work.
        """
        if "all_features" in d:
            d = {**d, "features": d["all_features"]}
        return d


@dataclass(frozen=True, slots=True)
class ShutdownOptions(Request):
    """ShutdownOptions model."""

    force: bool


@dataclass(frozen=True, slots=True)
class RebootOptions(Request):
    """RebootOptions model."""

    force: bool


@dataclass(frozen=True, slots=True)
class HostOptions(Request):
    """HostOptions model."""

    hostname: str


@dataclass(frozen=True, slots=True)
class Service(ResponseData):
    """Service model."""

    name: str
    description: str
    state: ServiceState | str


@dataclass(frozen=True, slots=True)
class ServiceList(ResponseData):
    """ServiceList model."""

    services: list[Service]


@dataclass(frozen=True, slots=True)
class DiskUsage(ResponseData):
    """DiskUsage model."""

    id: str
    used_bytes: int
    label: str | None = None
    total_bytes: int | None = None
    children: list["DiskUsage"] | None = None


@dataclass(frozen=True, slots=True)
class LogsOptions:
    """LogsOptions model.

    lines is the number of lines from the end of the log to return, range is a
    journal Range header such as "entries=:-99:100" or "realtime=<from>:<to>:<n>".
    lines takes precedence over range. With no_colors ANSI color codes are removed.
    """

    lines: int | None = None
    format: LogFormat | None = None
    no_colors: bool = False
    range: str | None = None


@dataclass(frozen=True, slots=True)
class LogBoots(ResponseData):
    """LogBoots model.

    Boot IDs of the host by offset, 0 is the current boot, -1 the one before.
    """

    boots: dict[int, str]


@dataclass(frozen=True, slots=True)
class LogIdentifiers(ResponseData):
    """LogIdentifiers model."""

    identifiers: list[str]
