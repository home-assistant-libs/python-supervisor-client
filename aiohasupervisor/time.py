"""Time client for supervisor."""

from .client import _SupervisorComponentClient
from .models.time import TimeInfo, TimeOptions


class TimeClient(_SupervisorComponentClient):
    """Handles time and date access in supervisor."""

    async def info(self) -> TimeInfo:
        """Get time configuration."""
        result = await self._client.get("time/info")
        return TimeInfo.from_dict(result.data)

    async def set_options(self, options: TimeOptions) -> None:
        """Set time configuration."""
        await self._client.post("time/options", json=options.to_dict())
