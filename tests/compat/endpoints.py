"""Map of Supervisor endpoints to the client methods that call them.

Used by check_responses.py to replay responses recorded by Supervisor's tests
through the client. Covers every client method that parses a JSON response plus
every JSON GET, so a recorded GET with no entry here or in OMITTED means the
client lacks it. Methods returning text or a stream are omitted since Supervisor
does not record those. Kept in sync with the client by
tests/test_compat_endpoints.py.
"""

from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import (
    DiscoveryConfig,
    PartialBackupOptions,
    PartialRestoreOptions,
)


@dataclass(frozen=True)
class Endpoint:
    """Supervisor endpoint and how to call it with the client."""

    method: str
    # Path relative to the API root as the client builds it, params in braces
    template: str
    # Calls the client method, params given in template order
    call: Callable[[SupervisorClient, list[str]], Awaitable[Any]]


async def _empty_stream() -> AsyncIterator[bytes]:
    """Empty backup upload stream."""
    yield b""


ENDPOINTS = [
    # Root
    Endpoint("GET", "info", lambda c, _: c.info()),
    Endpoint("GET", "available_updates", lambda c, _: c.available_updates()),
    # Addons
    Endpoint("GET", "addons", lambda c, _: c.addons.list()),
    Endpoint("GET", "addons/{addon}/info", lambda c, p: c.addons.addon_info(p[0])),
    Endpoint(
        "GET", "addons/{addon}/options/config", lambda c, p: c.addons.addon_config(p[0])
    ),
    Endpoint(
        "POST",
        "addons/{addon}/options/validate",
        lambda c, p: c.addons.addon_config_validate(p[0], {}),
    ),
    Endpoint("GET", "addons/{addon}/stats", lambda c, p: c.addons.addon_stats(p[0])),
    # Backups
    Endpoint("GET", "backups", lambda c, _: c.backups.list()),
    Endpoint("GET", "backups/info", lambda c, _: c.backups.info()),
    Endpoint("POST", "backups/new/full", lambda c, _: c.backups.full_backup()),
    Endpoint(
        "POST",
        "backups/new/partial",
        lambda c, _: c.backups.partial_backup(PartialBackupOptions(homeassistant=True)),
    ),
    Endpoint(
        "POST",
        "backups/new/upload",
        lambda c, _: c.backups.upload_backup(_empty_stream()),
    ),
    Endpoint("GET", "backups/{backup}/info", lambda c, p: c.backups.backup_info(p[0])),
    Endpoint(
        "POST",
        "backups/{backup}/restore/full",
        lambda c, p: c.backups.full_restore(p[0]),
    ),
    Endpoint(
        "POST",
        "backups/{backup}/restore/partial",
        lambda c, p: c.backups.partial_restore(
            p[0], PartialRestoreOptions(homeassistant=True)
        ),
    ),
    # Discovery
    Endpoint("GET", "discovery", lambda c, _: c.discovery.list()),
    Endpoint(
        "POST",
        "discovery",
        lambda c, _: c.discovery.set(DiscoveryConfig(service="compat", config={})),
    ),
    Endpoint("GET", "discovery/{uuid}", lambda c, p: c.discovery.get(UUID(p[0]))),
    # Home Assistant
    Endpoint("GET", "core/info", lambda c, _: c.homeassistant.info()),
    Endpoint("GET", "core/stats", lambda c, _: c.homeassistant.stats()),
    # Host
    Endpoint("GET", "host/info", lambda c, _: c.host.info()),
    Endpoint("GET", "host/services", lambda c, _: c.host.services()),
    Endpoint("GET", "host/disks/default/usage", lambda c, _: c.host.get_disk_usage()),
    # Ingress
    Endpoint("GET", "ingress/panels", lambda c, _: c.ingress.panels()),
    Endpoint("POST", "ingress/session", lambda c, _: c.ingress.create_session()),
    # Jobs
    Endpoint("GET", "jobs/info", lambda c, _: c.jobs.info()),
    Endpoint("GET", "jobs/{job}", lambda c, p: c.jobs.get_job(UUID(p[0]))),
    # Mounts
    Endpoint("GET", "mounts", lambda c, _: c.mounts.info()),
    # Network
    Endpoint("GET", "network/info", lambda c, _: c.network.info()),
    Endpoint(
        "GET",
        "network/interface/{interface}/info",
        lambda c, p: c.network.interface_info(p[0]),
    ),
    Endpoint(
        "GET",
        "network/interface/{interface}/accesspoints",
        lambda c, p: c.network.access_points(p[0]),
    ),
    # OS
    Endpoint("GET", "os/info", lambda c, _: c.os.info()),
    Endpoint("GET", "os/config/swap", lambda c, _: c.os.swap_info()),
    Endpoint("GET", "os/datadisk/list", lambda c, _: c.os.list_data_disks()),
    Endpoint("GET", "os/boards/green", lambda c, _: c.os.green_info()),
    Endpoint("GET", "os/boards/yellow", lambda c, _: c.os.yellow_info()),
    Endpoint(
        "GET",
        "os/boards/raspberrypi/firmware",
        lambda c, _: c.os.raspberry_pi_firmware_info(),
    ),
    # Resolution
    Endpoint("GET", "resolution/info", lambda c, _: c.resolution.info()),
    Endpoint(
        "GET",
        "resolution/issue/{issue}/suggestions",
        lambda c, p: c.resolution.suggestions_for_issue(UUID(p[0])),
    ),
    # Store
    Endpoint("GET", "store", lambda c, _: c.store.info()),
    Endpoint("GET", "store/addons", lambda c, _: c.store.addons_list()),
    Endpoint("GET", "store/addons/{addon}", lambda c, p: c.store.addon_info(p[0])),
    Endpoint(
        "GET",
        "store/addons/{addon}/availability",
        lambda c, p: c.store.addon_availability(p[0]),
    ),
    Endpoint("GET", "store/repositories", lambda c, _: c.store.repositories_list()),
    Endpoint(
        "GET",
        "store/repositories/{repository}",
        lambda c, p: c.store.repository_info(p[0]),
    ),
    # Supervisor
    Endpoint("GET", "supervisor/ping", lambda c, _: c.supervisor.ping()),
    Endpoint("GET", "supervisor/info", lambda c, _: c.supervisor.info()),
    Endpoint("GET", "supervisor/stats", lambda c, _: c.supervisor.stats()),
    # Time
    Endpoint("GET", "time/info", lambda c, _: c.time.info()),
]

# Supervisor endpoints the client intentionally omits, as glob patterns matched
# against templates without a leading slash and with each param replaced by "*".
# Not reported as client gaps when checking coverage.
OMITTED = [
    # Log endpoints, omitted for now (AddonsClient, HostClient)
    "*/logs",
    "*/logs/*",
    # Icon/logo endpoints, omitted for now (StoreClient)
    "*/icon",
    "*/logo",
    # Ingress proxy to apps, can't be modeled (IngressClient)
    "ingress/*/*",
]
