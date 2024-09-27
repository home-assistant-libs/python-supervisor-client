"""Test Home Assistant supervisor client."""

from aioresponses import aioresponses
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import HomeAssistantOptions

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_homeassistant_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Home Assistant info API."""
    responses.get(
        f"{SUPERVISOR_URL}/core/info",
        status=200,
        body=load_fixture("homeassistant_info.json"),
    )
    info = await supervisor_client.homeassistant.info()

    assert info.version == "2024.9.0"
    assert info.update_available is False
    assert info.arch == "aarch64"
    assert info.ssl is False
    assert info.port == 8123
    assert info.audio_output is None


async def test_homeassistant_stats(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Home Assistant stats API."""
    responses.get(
        f"{SUPERVISOR_URL}/core/stats",
        status=200,
        body=load_fixture("homeassistant_stats.json"),
    )
    stats = await supervisor_client.homeassistant.stats()

    assert stats.cpu_percent == 0.01
    assert stats.memory_usage == 678883328
    assert stats.memory_percent == 17.41


async def test_homeassistant_options(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Home Assistant options API."""
    responses.post(f"{SUPERVISOR_URL}/core/options", status=200)
    assert (
        await supervisor_client.homeassistant.options(
            HomeAssistantOptions(watchdog=False, backups_exclude_database=True)
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/core/options"))
    }


async def test_homeassistant_update(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Home Assistant update API."""
    responses.post(f"{SUPERVISOR_URL}/core/update", status=200)
    assert await supervisor_client.homeassistant.update() is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/core/update"))}


async def test_homeassistant_restart(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Home Assistant restart API."""
    responses.post(f"{SUPERVISOR_URL}/core/restart", status=200)
    assert await supervisor_client.homeassistant.restart() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/core/restart"))
    }


async def test_homeassistant_stop(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Home Assistant stop API."""
    responses.post(f"{SUPERVISOR_URL}/core/stop", status=200)
    assert await supervisor_client.homeassistant.stop() is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/core/stop"))}


async def test_homeassistant_start(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Home Assistant start API."""
    responses.post(f"{SUPERVISOR_URL}/core/start", status=200)
    assert await supervisor_client.homeassistant.start() is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/core/start"))}


async def test_homeassistant_check_config(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Home Assistant check config API."""
    responses.post(f"{SUPERVISOR_URL}/core/check", status=200)
    assert await supervisor_client.homeassistant.check_config() is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/core/check"))}


async def test_homeassistant_rebuild(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Home Assistant rebuild API."""
    responses.post(f"{SUPERVISOR_URL}/core/rebuild", status=200)
    assert await supervisor_client.homeassistant.rebuild() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/core/rebuild"))
    }