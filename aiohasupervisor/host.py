"""Host client for supervisor."""

import re
from urllib.parse import quote

from .client import _SupervisorComponentClient
from .const import TIMEOUT_60_SECONDS
from .exceptions import SupervisorError
from .models.host import (
    HostInfo,
    HostOptions,
    NVMeStatus,
    RebootOptions,
    Service,
    ServiceList,
    ShutdownOptions,
)

RE_NVME_DEVICE = re.compile(r"^(?:[-A-Fa-f0-9]+|\/dev\/[-_a-z0-9]+)$")


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

    async def nvme_status(self, device: str | None = None) -> NVMeStatus:
        """Get NVMe status for a device.

        Device can be the Host ID or device path (e.g. /dev/nvme0n1).
        If omitted, returns status of datadisk if it is an nvme device.
        """
        if device is not None:
            # Encoding must be done here because something like /dev/nvme0n1 is
            # valid and that won't work in the resource path. But that means we
            # bypass part of the safety check that would normally raise on any
            # encoded chars. So strict validation needs to be done here rather
            # then letting Supervisor handle it like normal.
            if not RE_NVME_DEVICE.match(device):
                raise SupervisorError(f"Invalid device: {device}")

            encoded = quote(device, safe="")
            result = await self._client.get(
                f"host/nvme/{encoded}/status", uri_encoded=True
            )
        else:
            result = await self._client.get("host/nvme/status")
        return NVMeStatus.from_dict(result.data)

    # Omitted for now - Log endpoints
