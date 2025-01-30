"""Models for Supervisor jobs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime  # noqa: TCH003
from enum import StrEnum
from uuid import UUID  # noqa: TCH003

from .base import Request, ResponseData

# --- ENUMS ----


class JobCondition(StrEnum):
    """JobCondition type.

    This is an incomplete list. Supervisor regularly adds support for new
    job conditions as they are found to be needed. Therefore when returning
    a list of job conditions, there may be some which are not in
    this list parsed as strings on older versions of the client.
    """

    AUTO_UPDATE = "auto_update"
    FREE_SPACE = "free_space"
    FROZEN = "frozen"
    HAOS = "haos"
    HEALTHY = "healthy"
    HOST_NETWORK = "host_network"
    INTERNET_HOST = "internet_host"
    INTERNET_SYSTEM = "internet_system"
    MOUNT_AVAILABLE = "mount_available"
    OS_AGENT = "os_agent"
    PLUGINS_UPDATED = "plugins_updated"
    RUNNING = "running"
    SUPERVISOR_UPDATED = "supervisor_updated"


# --- OBJECTS ----


@dataclass(slots=True, frozen=True)
class JobError(ResponseData):
    """JobError model."""

    type: str
    message: str


@dataclass(slots=True, frozen=True)
class Job(ResponseData):
    """Job model."""

    name: str | None
    reference: str | None
    uuid: UUID
    progress: float
    stage: str | None
    done: bool | None
    errors: list[JobError]
    created: datetime
    child_jobs: list[Job]


@dataclass(slots=True, frozen=True)
class JobsInfo(ResponseData):
    """JobsInfo model."""

    ignore_conditions: list[JobCondition | str]
    jobs: list[Job]


@dataclass(slots=True, frozen=True)
class JobsOptions(Request):
    """JobsOptions model."""

    # We only do `| str` in responses since we can't control what supervisor returns
    # Support for ignoring new job conditions will wait for a new version of library
    ignore_conditions: list[JobCondition]
