"""Backups client for supervisor."""

from .client import _SupervisorComponentClient
from .const import ResponseType
from .models.backups import (
    Backup,
    BackupComplete,
    BackupJob,
    BackupList,
    BackupsInfo,
    BackupsOptions,
    FreezeOptions,
    FullBackupOptions,
    FullRestoreOptions,
    NewBackup,
    PartialBackupOptions,
    PartialRestoreOptions,
)


class BackupsClient(_SupervisorComponentClient):
    """Handles backups access in Supervisor."""

    async def list(self) -> list[Backup]:
        """List backups."""
        result = await self._client.get("backups")
        return BackupList.from_dict(result.data).backups

    async def info(self) -> BackupsInfo:
        """Get backups info."""
        result = await self._client.get("backups/info")
        return BackupsInfo.from_dict(result.data)

    async def options(self, options: BackupsOptions) -> None:
        """Set options for backups."""
        await self._client.post("backups/options", json=options.to_dict())

    async def reload(self) -> None:
        """Reload backups cache."""
        await self._client.post("backups/reload")

    async def freeze(self, options: FreezeOptions | None = None) -> None:
        """Start a freeze for external snapshot process."""
        await self._client.post(
            "backups/freeze", json=options.to_dict() if options else None
        )

    async def thaw(self) -> None:
        """Thaw an active freeze when external snapshot process ends."""
        await self._client.post("backups/thaw")

    async def full_backup(self, options: FullBackupOptions | None = None) -> NewBackup:
        """Create a new full backup."""
        result = await self._client.post(
            "backups/new/full",
            json=options.to_dict() if options else None,
            response_type=ResponseType.JSON,
        )
        return NewBackup.from_dict(result.data)

    async def partial_backup(self, options: PartialBackupOptions) -> NewBackup:
        """Create a new partial backup."""
        result = await self._client.post(
            "backups/new/partial",
            json=options.to_dict(),
            response_type=ResponseType.JSON,
        )
        return NewBackup.from_dict(result.data)

    async def backup_info(self, backup: str) -> BackupComplete:
        """Get backup details."""
        result = await self._client.get(f"backups/{backup}/info")
        return BackupComplete.from_dict(result.data)

    async def remove_backup(self, backup: str) -> None:
        """Remove a backup."""
        await self._client.delete(f"backups/{backup}")

    async def full_restore(
        self, backup: str, options: FullRestoreOptions | None = None
    ) -> BackupJob:
        """Start full restore from backup."""
        result = await self._client.post(
            f"backups/{backup}/restore/full",
            json=options.to_dict() if options else None,
            response_type=ResponseType.JSON,
        )
        return BackupJob.from_dict(result.data)

    async def partial_restore(
        self, backup: str, options: PartialRestoreOptions
    ) -> BackupJob:
        """Start partial restore from backup."""
        result = await self._client.post(
            f"backups/{backup}/restore/partial",
            json=options.to_dict(),
            response_type=ResponseType.JSON,
        )
        return BackupJob.from_dict(result.data)

    # Omitted for now - Upload and download backup
