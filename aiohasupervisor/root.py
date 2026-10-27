"""Main client for supervisor."""

from pathlib import Path
from typing import Self

from aiohttp import ClientSession, ClientTimeout

from .addons import AddonsClient
from .backups import BackupsClient
from .client import _SupervisorClient
from .const import DEFAULT_UNIX_SOCKET_API_HOST
from .discovery import DiscoveryClient
from .homeassistant import HomeAssistantClient
from .host import HostClient
from .ingress import IngressClient
from .jobs import JobsClient
from .models.root import AvailableUpdate, AvailableUpdates, RootInfo
from .mounts import MountsClient
from .network import NetworkClient
from .os import OSClient
from .resolution import ResolutionClient
from .store import StoreClient
from .supervisor import SupervisorManagementClient
from .time import TimeClient


class SupervisorClient:
    """Main supervisor client for all Supervisor access."""

    def __init__(
        self,
        api_host: str | None = None,
        token: str | None = None,
        session: ClientSession | None = None,
        *,
        source: str | None = None,
        unix_socket: Path | None = None,
    ) -> None:
        """Initialize client.

        Optional source is sent as the X-Hass-Source header on all requests. It is
        intended for Home Assistant Core to identify itself.

        Optional unix_socket is the path of a Unix socket to reach Supervisor on.
        Supervisor identifies the caller by the socket, so a token cannot be passed.
        If a session is passed it must already use a connector for that socket.
        api_host defaults to http://localhost in this case.
        """
        if unix_socket is None:
            if api_host is None or token is None:
                raise ValueError("api_host and token are required without unix_socket")
        elif token is not None:
            raise ValueError("token cannot be used with unix_socket")
        elif api_host is None:
            api_host = DEFAULT_UNIX_SOCKET_API_HOST
        self._client = _SupervisorClient(api_host, token, session, source, unix_socket)
        self._addons = AddonsClient(self._client)
        self._os = OSClient(self._client)
        self._backups = BackupsClient(self._client)
        self._discovery = DiscoveryClient(self._client)
        self._jobs = JobsClient(self._client)
        self._mounts = MountsClient(self._client)
        self._network = NetworkClient(self._client)
        self._host = HostClient(self._client)
        self._resolution = ResolutionClient(self._client)
        self._store = StoreClient(self._client)
        self._supervisor = SupervisorManagementClient(self._client)
        self._homeassistant = HomeAssistantClient(self._client)
        self._ingress = IngressClient(self._client)
        self._time = TimeClient(self._client)

    @property
    def addons(self) -> AddonsClient:
        """Get addons component client."""
        return self._addons

    @property
    def homeassistant(self) -> HomeAssistantClient:
        """Get Home Assistant component client."""
        return self._homeassistant

    @property
    def os(self) -> OSClient:
        """Get OS component client."""
        return self._os

    @property
    def backups(self) -> BackupsClient:
        """Get backups component client."""
        return self._backups

    @property
    def discovery(self) -> DiscoveryClient:
        """Get discovery component client."""
        return self._discovery

    @property
    def jobs(self) -> JobsClient:
        """Get jobs component client."""
        return self._jobs

    @property
    def mounts(self) -> MountsClient:
        """Get mounts component client."""
        return self._mounts

    @property
    def network(self) -> NetworkClient:
        """Get network component client."""
        return self._network

    @property
    def time(self) -> TimeClient:
        """Get time component client."""
        return self._time

    @property
    def host(self) -> HostClient:
        """Get host component client."""
        return self._host

    @property
    def resolution(self) -> ResolutionClient:
        """Get resolution center component client."""
        return self._resolution

    @property
    def store(self) -> StoreClient:
        """Get store component client."""
        return self._store

    @property
    def supervisor(self) -> SupervisorManagementClient:
        """Get supervisor component client."""
        return self._supervisor

    @property
    def ingress(self) -> IngressClient:
        """Get ingress component client."""
        return self._ingress

    async def info(self) -> RootInfo:
        """Get root info."""
        result = await self._client.get("info")
        return RootInfo.from_dict(result.data)

    async def reload_updates(self) -> None:
        """Reload updates.

        Reload main components update information (OS, Supervisor, Core and plug-ins).
        """
        await self._client.post("reload_updates", timeout=ClientTimeout(total=300))

    async def refresh_updates(self) -> None:
        """Refresh updates.

        Discouraged as this endpoint does two things at once. Use the `reload_updates()`
        and `store.reload()` instead.
        """
        await self._client.post("refresh_updates", timeout=ClientTimeout(total=300))

    async def available_updates(self) -> list[AvailableUpdate]:
        """Get available updates."""
        result = await self._client.get("available_updates")
        return AvailableUpdates.from_dict(result.data).available_updates

    async def close(self) -> None:
        """Close open client session."""
        await self._client.close()

    async def __aenter__(self) -> Self:
        """Async enter, closes session on exit."""
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Close session."""
        await self.close()
