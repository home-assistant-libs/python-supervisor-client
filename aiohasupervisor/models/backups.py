"""Models for Supervisor backups."""

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import PurePath
from uuid import UUID

from .base import Options, Request, ResponseData

LOCATION_LOCAL_STORAGE = ".local"
LOCATION_CLOUD_BACKUP = ".cloud_backup"

# --- ENUMS ----


class BackupType(StrEnum):
    """BackupType type."""

    FULL = "full"
    PARTIAL = "partial"


class Folder(StrEnum):
    """Folder type."""

    SHARE = "share"
    ADDONS = "addons/local"
    SSL = "ssl"
    MEDIA = "media"


class AddonSet(StrEnum):
    """AddonSet type."""

    ALL = "ALL"


# --- OBJECTS ----


@dataclass(frozen=True, slots=True)
class BackupContent(ResponseData):
    """BackupContent model."""

    homeassistant: bool
    addons: list[str]
    folders: list[Folder]


@dataclass(frozen=True, slots=True)
class BackupLocationAttributes(ResponseData):
    """BackupLocationAttributes model."""

    protected: bool
    size_bytes: int


@dataclass(frozen=True)
class BackupBaseFields(ABC):
    """BackupBaseFields ABC type."""

    slug: str
    name: str
    date: datetime
    type: BackupType
    location_attributes: dict[str, BackupLocationAttributes]
    compressed: bool


@dataclass(frozen=True, slots=True)
class Backup(BackupBaseFields, ResponseData):
    """Backup model."""

    content: BackupContent


@dataclass(frozen=True, slots=True)
class BackupAddon(ResponseData):
    """BackupAddon model."""

    slug: str
    name: str
    version: str
    size: float


@dataclass(frozen=True, slots=True)
class BackupComplete(BackupBaseFields, ResponseData):
    """BackupComplete model."""

    supervisor_version: str
    homeassistant: str | None
    addons: list[BackupAddon]
    repositories: list[str]
    folders: list[Folder]
    homeassistant_exclude_database: bool | None
    extra: dict | None


@dataclass(frozen=True, slots=True)
class BackupList(ResponseData):
    """BackupList model."""

    backups: list[Backup]


@dataclass(frozen=True, slots=True)
class BackupsInfo(BackupList):
    """BackupsInfo model."""

    days_until_stale: int


@dataclass(frozen=True, slots=True)
class BackupsOptions(Request):
    """BackupsOptions model."""

    days_until_stale: int


@dataclass(frozen=True, slots=True)
class FreezeOptions(Request):
    """FreezeOptions model."""

    timeout: int


@dataclass(frozen=True)
class PartialBackupRestoreOptions(ABC):  # noqa: B024
    """PartialBackupRestoreOptions ABC type."""

    addons: set[str] | None = None
    folders: set[Folder] | None = None
    homeassistant: bool | None = None

    def __post_init__(self) -> None:
        """Validate at least one thing to backup/restore is included."""
        if not any((self.addons, self.folders, self.homeassistant)):
            raise ValueError(
                "At least one of addons, folders, or homeassistant must have a value"
            )


@dataclass(frozen=True, slots=True)
class FullBackupOptions(Request):
    """FullBackupOptions model."""

    name: str | None = None
    password: str | None = None
    compressed: bool | None = None
    location: str | list[str] = None  # type: ignore[assignment]
    homeassistant_exclude_database: bool | None = None
    background: bool | None = None
    extra: dict | None = None
    filename: PurePath | None = None


@dataclass(frozen=True, slots=True)
class PartialBackupOptions(FullBackupOptions, PartialBackupRestoreOptions):
    """PartialBackupOptions model."""

    addons: AddonSet | set[str] | None = None


@dataclass(frozen=True, slots=True)
class BackupJob(ResponseData):
    """BackupJob model."""

    job_id: UUID


@dataclass(frozen=True, slots=True)
class NewBackup(BackupJob):
    """NewBackup model."""

    slug: str | None = None


@dataclass(frozen=True, slots=True)
class FullRestoreOptions(Request):
    """FullRestoreOptions model."""

    password: str | None = None
    background: bool | None = None
    location: str = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class PartialRestoreOptions(FullRestoreOptions, PartialBackupRestoreOptions):
    """PartialRestoreOptions model."""


@dataclass(frozen=True, slots=True)
class UploadBackupOptions(Options):
    """UploadBackupOptions model."""

    location: set[str] = None
    filename: PurePath | None = None


@dataclass(frozen=True, slots=True)
class UploadedBackup(ResponseData):
    """UploadedBackup model."""

    slug: str


@dataclass(frozen=True, slots=True)
class RemoveBackupOptions(Request):
    """RemoveBackupOptions model."""

    location: set[str] = None


@dataclass(frozen=True, slots=True)
class DownloadBackupOptions(Request):
    """DownloadBackupOptions model."""

    location: str = None  # type: ignore[assignment]
