"""Home Assistant client for supervisor."""

from .client import _SupervisorComponentClient
from .models.homeassistant import (
    HomeAssistantInfo,
    HomeAssistantOptions,
    HomeAssistantRebuildOptions,
    HomeAssistantRestartOptions,
    HomeAssistantStats,
    HomeAssistantStopOptions,
    HomeAssistantUpdateOptions,
)
from .models.host import LogsOptions
from .utils.aiohttp import ResponseLineIterator


class HomeAssistantClient(_SupervisorComponentClient):
    """Handles Home Assistant access in supervisor."""

    async def info(self) -> HomeAssistantInfo:
        """Get Home Assistant info."""
        result = await self._client.get("core/info")
        return HomeAssistantInfo.from_dict(result.data)

    async def stats(self) -> HomeAssistantStats:
        """Get Home Assistant stats."""
        result = await self._client.get("core/stats")
        return HomeAssistantStats.from_dict(result.data)

    async def set_options(self, options: HomeAssistantOptions) -> None:
        """Set Home Assistant options."""
        await self._client.post("core/options", json=options.to_dict())

    async def update(self, options: HomeAssistantUpdateOptions | None = None) -> None:
        """Update Home Assistant."""
        await self._client.post(
            "core/update", json=options.to_dict() if options else None, timeout=None
        )

    async def restart(self, options: HomeAssistantRestartOptions | None = None) -> None:
        """Restart Home Assistant."""
        await self._client.post(
            "core/restart",
            json=options.to_dict() if options else None,
            timeout=None,
        )

    async def stop(self, options: HomeAssistantStopOptions | None = None) -> None:
        """Stop Home Assistant."""
        await self._client.post(
            "core/stop", json=options.to_dict() if options else None, timeout=None
        )

    async def start(self) -> None:
        """Start Home Assistant."""
        await self._client.post("core/start", timeout=None)

    async def check_config(self) -> None:
        """Check Home Assistant config."""
        await self._client.post("core/check")

    async def rebuild(self, options: HomeAssistantRebuildOptions | None = None) -> None:
        """Rebuild Home Assistant."""
        await self._client.post(
            "core/rebuild",
            json=options.to_dict() if options else None,
            timeout=None,
        )

    async def logs(
        self,
        options: LogsOptions | None = None,
        *,
        boot: int | str | None = None,
        follow: bool = False,
        latest: bool = False,
    ) -> ResponseLineIterator:
        """Stream the Home Assistant log.

        boot is a boot ID or an offset, 0 is the current boot and -1 the one before.
        latest returns the log since the container last started, without colors.
        """
        return await self._logs(
            "core/logs", options, boot=boot, follow=follow, latest=latest
        )
