"""Host client for supervisor."""

from .client import _SupervisorComponentClient
from .const import TIMEOUT_60_SECONDS
from .models.host import (
    DiskUsage,
    HostInfo,
    HostOptions,
    LogBoots,
    LogIdentifiers,
    LogsOptions,
    RebootOptions,
    Service,
    ServiceList,
    ShutdownOptions,
)
from .utils.aiohttp import ResponseLineIterator


class HostClient(_SupervisorComponentClient):
    """Handles host access in supervisor."""

    async def info(self) -> HostInfo:
        """Get host info."""
        result = await self._client.get("host/info")
        return HostInfo.from_dict(result.data)

    async def reboot(self, options: RebootOptions | None = None) -> None:
        """Reboot host."""
        await self._client.post(
            "host/reboot",
            json=options.to_dict() if options else None,
            timeout=TIMEOUT_60_SECONDS,
        )

    async def shutdown(self, options: ShutdownOptions | None = None) -> None:
        """Shutdown host."""
        await self._client.post(
            "host/shutdown", json=options.to_dict() if options else None
        )

    async def reload(self) -> None:
        """Reload host info cache."""
        await self._client.post("host/reload")

    async def set_options(self, options: HostOptions) -> None:
        """Set host options."""
        await self._client.post("host/options", json=options.to_dict())

    async def services(self) -> list[Service]:
        """Get list of available services on host."""
        result = await self._client.get("host/services")
        return ServiceList.from_dict(result.data).services

    async def get_disk_usage(self, max_depth: int = 1) -> DiskUsage:
        """Get disk usage."""
        result = await self._client.get(
            "host/disks/default/usage",
            params={"max_depth": str(max_depth)},
        )
        return DiskUsage.from_dict(result.data)

    async def logs(
        self,
        options: LogsOptions | None = None,
        *,
        identifier: str | None = None,
        boot: int | str | None = None,
        follow: bool = False,
    ) -> ResponseLineIterator:
        """Stream the host log, limited to a syslog identifier and a boot if given.

        boot is a boot ID or an offset, 0 is the current boot and -1 the one before.
        """
        uri = "host/logs"
        if boot is not None:
            uri = f"{uri}/boots/{boot}"
        if identifier is not None:
            uri = f"{uri}/identifiers/{identifier}"
        return await self._logs(uri, options, follow=follow)

    async def log_boots(self) -> dict[int, str]:
        """Get boot IDs by offset, 0 is the current boot and -1 the one before."""
        result = await self._client.get("host/logs/boots")
        return LogBoots.from_dict(result.data).boots

    async def log_identifiers(self) -> list[str]:
        """Get syslog identifiers in the host log."""
        result = await self._client.get("host/logs/identifiers")
        return LogIdentifiers.from_dict(result.data).identifiers
