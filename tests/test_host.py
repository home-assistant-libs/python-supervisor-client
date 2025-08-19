"""Test host supervisor client."""

from datetime import UTC, datetime

from aioresponses import aioresponses
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import HostOptions, RebootOptions, ShutdownOptions

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_host_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test host info API."""
    responses.get(
        f"{SUPERVISOR_URL}/host/info", status=200, body=load_fixture("host_info.json")
    )
    result = await supervisor_client.host.info()
    assert result.agent_version == "1.6.0"
    assert result.chassis == "embedded"
    assert result.virtualization == ""
    assert result.disk_total == 27.9
    assert result.disk_life_time == 10
    assert result.features == [
        "reboot",
        "shutdown",
        "services",
        "network",
        "hostname",
        "timedate",
        "os_agent",
        "haos",
        "resolved",
        "journal",
        "disk",
        "mount",
    ]
    assert result.hostname == "homeassistant"
    assert result.llmnr_hostname == "homeassistant3"
    assert result.dt_utc == datetime(2024, 10, 3, 0, 0, 0, 0, UTC)
    assert result.dt_synchronized is True
    assert result.startup_time == 1.966311


@pytest.mark.parametrize("options", [None, RebootOptions(force=True)])
async def test_host_reboot(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: RebootOptions | None,
) -> None:
    """Test host reboot API."""
    responses.post(f"{SUPERVISOR_URL}/host/reboot", status=200)
    assert await supervisor_client.host.reboot(options) is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/host/reboot"))}


@pytest.mark.parametrize("options", [None, ShutdownOptions(force=True)])
async def test_host_shutdown(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: ShutdownOptions | None,
) -> None:
    """Test host shutdown API."""
    responses.post(f"{SUPERVISOR_URL}/host/shutdown", status=200)
    assert await supervisor_client.host.shutdown(options) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/host/shutdown"))
    }


async def test_host_reload(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test host reload API."""
    responses.post(f"{SUPERVISOR_URL}/host/reload", status=200)
    assert await supervisor_client.host.reload() is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/host/reload"))}


async def test_host_options(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test host options API."""
    responses.post(f"{SUPERVISOR_URL}/host/options", status=200)
    assert (
        await supervisor_client.host.set_options(HostOptions(hostname="test")) is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/host/options"))
    }


async def test_host_services(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test host services API."""
    responses.get(
        f"{SUPERVISOR_URL}/host/services",
        status=200,
        body=load_fixture("host_services.json"),
    )
    result = await supervisor_client.host.services()
    assert result[0].name == "emergency.service"
    assert result[0].description == "Emergency Shell"
    assert result[0].state == "inactive"
    assert result[-1].name == "systemd-resolved.service"
    assert result[-1].description == "Network Name Resolution"
    assert result[-1].state == "active"


async def test_host_disk_usage(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test host disk usage API."""
    responses.get(
        f"{SUPERVISOR_URL}/host/disks/default/usage?max_depth=1",
        status=200,
        body=load_fixture("host_disk_usage.json"),
    )
    result = await supervisor_client.host.get_disk_usage()

    # Test top-level properties
    assert result.total_bytes == 503312781312
    assert result.used_bytes == 430243422208
    assert result.children is not None

    # Test children structure
    children = result.children
    assert children is not None
    assert len(children) == 8  # Should have 8 children

    # Find specific children by id
    assert (
        addons_data := next(child for child in children if child.id == "addons_data")
    )
    assert next(child for child in children if child.id == "addons_config")
    assert next(child for child in children if child.id == "media")
    assert next(child for child in children if child.id == "share")
    assert (backup := next(child for child in children if child.id == "backup"))
    assert next(child for child in children if child.id == "ssl")
    assert (
        homeassistant := next(
            child for child in children if child.id == "homeassistant"
        )
    )
    assert next(child for child in children if child.id == "system")

    # Test nested children (recursive structure)
    assert addons_data.used_bytes == 42347618720
    assert addons_data.children is not None
    assert len(addons_data.children) == 4

    # Find specific nested children
    assert next(
        child for child in addons_data.children if child.id == "77f1785d_remote_api"
    )
    assert next(child for child in addons_data.children if child.id == "core_samba")
    assert (
        plex_addon := next(
            child for child in addons_data.children if child.id == "a0d7b954_plex"
        )
    )
    assert next(child for child in addons_data.children if child.id == "core_whisper")

    # Test deeper nesting
    assert plex_addon.used_bytes == 757750613
    assert plex_addon.children is None  # Leaf node

    # Test another branch
    assert homeassistant.used_bytes == 444089236
    assert homeassistant.children is not None
    assert len(homeassistant.children) == 3

    # Find specific homeassistant children
    assert next(child for child in homeassistant.children if child.id == "image")
    assert next(
        child for child in homeassistant.children if child.id == "custom_components"
    )
    assert next(child for child in homeassistant.children if child.id == "www")

    # Test leaf node without children
    assert backup.used_bytes == 268350699520
    assert backup.children is None


async def test_host_disk_usage_with_custom_depth(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test host disk usage API with custom max_depth."""
    responses.get(
        f"{SUPERVISOR_URL}/host/disks/default/usage?max_depth=3",
        status=200,
        body=load_fixture("host_disk_usage.json"),
    )
    result = await supervisor_client.host.get_disk_usage(max_depth=3)

    # Test that the custom max_depth parameter was used
    assert result.total_bytes == 503312781312
    assert result.used_bytes == 430243422208
