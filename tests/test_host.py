"""Test host supervisor client."""

from datetime import UTC, datetime
from pathlib import PurePath
from urllib.parse import quote

from aioresponses import aioresponses
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.exceptions import SupervisorError
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
    assert result.nvme_devices[0].id == "00000000-0000-0000-0000-000000000000"
    assert result.nvme_devices[0].path == PurePath("/dev/nvme0n1")


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


async def test_host_nvme_status(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test host nvme_status API."""
    responses.get(
        f"{SUPERVISOR_URL}/host/nvme/status",
        status=200,
        body=load_fixture("host_nvme_status.json"),
    )
    result = await supervisor_client.host.nvme_status()
    assert result.available_spare == 100
    assert result.critical_warning == 0
    assert result.data_units_read == 44707691
    assert result.data_units_written == 54117388
    assert result.percent_used == 1
    assert result.temperature_kelvin == 312
    assert result.host_read_commands == 428871098
    assert result.host_write_commands == 900245782
    assert result.controller_busy_minutes == 2678
    assert result.power_cycles == 652
    assert result.power_on_hours == 3192
    assert result.unsafe_shutdowns == 107
    assert result.media_errors == 0
    assert result.number_error_log_entries == 1069
    assert result.warning_temp_minutes == 0
    assert result.critical_composite_temp_minutes == 0


@pytest.mark.parametrize("device", ["1234-5678", "/dev/nvme0n1"])
async def test_host_nvme_status_device(
    responses: aioresponses, supervisor_client: SupervisorClient, device: str
) -> None:
    """Test host nvme_status API with device argument."""
    encoded = quote(device, safe="")
    responses.get(
        f"{SUPERVISOR_URL}/host/nvme/{encoded}/status",
        status=200,
        body=load_fixture("host_nvme_status.json"),
    )
    result = await supervisor_client.host.nvme_status(device)
    assert result.available_spare == 100
    assert result.critical_warning == 0
    assert result.data_units_read == 44707691
    assert result.data_units_written == 54117388
    assert result.percent_used == 1
    assert result.temperature_kelvin == 312
    assert result.host_read_commands == 428871098
    assert result.host_write_commands == 900245782
    assert result.controller_busy_minutes == 2678
    assert result.power_cycles == 652
    assert result.power_on_hours == 3192
    assert result.unsafe_shutdowns == 107
    assert result.media_errors == 0
    assert result.number_error_log_entries == 1069
    assert result.warning_temp_minutes == 0
    assert result.critical_composite_temp_minutes == 0


@pytest.mark.parametrize(
    "device", ["/test/../bad", "test/../bad", "test/%2E%2E/bad", "/dev/../bad"]
)
async def test_host_nvme_status_path_manipulation_blocked(
    supervisor_client: SupervisorClient, device: str
) -> None:
    """Test path manipulation prevented."""
    with pytest.raises(SupervisorError, match=r"^Invalid device: "):
        await supervisor_client.host.nvme_status(device)
