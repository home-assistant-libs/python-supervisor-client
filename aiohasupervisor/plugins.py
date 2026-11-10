"""Plugins client for supervisor."""

from .client import _SupervisorComponentClient
from .models.host import LogsOptions
from .models.plugins import Plugin
from .utils.aiohttp import ResponseLineIterator


class PluginsClient(_SupervisorComponentClient):
    """Handles plugin access in Supervisor."""

    async def logs(
        self,
        plugin: Plugin,
        options: LogsOptions | None = None,
        *,
        boot: int | str | None = None,
        follow: bool = False,
        latest: bool = False,
    ) -> ResponseLineIterator:
        """Stream the log of a plugin.

        boot is a boot ID or an offset, 0 is the current boot and -1 the one before.
        latest returns the log since the container last started, without colors.
        """
        return await self._logs(
            f"{plugin}/logs", options, boot=boot, follow=follow, latest=latest
        )
