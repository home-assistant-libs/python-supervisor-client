"""NTP client for supervisor."""

from .client import _SupervisorComponentClient
from .models.ntp import NTPInfo, NTPOptions


class NTPClient(_SupervisorComponentClient):
    """Handles NTP access in supervisor."""

    async def info(self) -> NTPInfo:
        """Get NTP server configuration."""
        result = await self._client.get("ntp/info")
        return NTPInfo.from_dict(result.data)

    async def set_options(self, options: NTPOptions) -> None:
        """Set NTP server configuration."""
        await self._client.post("ntp/options", json=options.to_dict())
