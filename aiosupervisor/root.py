"""Main client for supervisor."""

from collections.abc import Awaitable
from typing import Self

from aiohttp import ClientSession

from .addons import AddonsClient
from .client import _SupervisorClient
from .models.root import AvailableUpdate, AvailableUpdates, RootInfo


class SupervisorClient:
    """Main supervisor client for all Supervisor access."""

    def __init__(
        self,
        api_host: str,
        token: str,
        request_timeout: int = 10,
        session: ClientSession | None = None,
    ) -> None:
        """Initialize client."""
        self._client = _SupervisorClient(api_host, token, request_timeout, session)
        self._addons = AddonsClient(self._client)

    @property
    def addons(self) -> AddonsClient:
        """Get addons component client."""
        return self._addons

    async def info(self) -> RootInfo:
        """Get root info."""
        result = await self._client.get("info")
        return RootInfo.from_dict(result.data)

    async def refresh_updates(self) -> None:
        """Refresh updates."""
        await self._client.post("refresh_updates")

    async def available_updates(self) -> list[AvailableUpdate]:
        """Get available updates."""
        result = await self._client.get("available_updates")
        return AvailableUpdates.from_dict(result.data).available_updates

    def close(self) -> Awaitable[None]:
        """Close open client session."""
        return self._client.close()

    async def __aenter__(self) -> Self:
        """Async enter, closes session on exit."""
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Close session."""
        await self.close()
