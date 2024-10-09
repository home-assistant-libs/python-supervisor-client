"""Test discovery supervisor client."""

from uuid import UUID

from aioresponses import aioresponses
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import DiscoveryConfig

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_discovery_list(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Discovery list API."""
    responses.get(
        f"{SUPERVISOR_URL}/discovery",
        status=200,
        body=load_fixture("discovery_list.json"),
    )
    disc_list = await supervisor_client.discovery.list()
    assert disc_list[0].addon == "core_mosquitto"
    assert disc_list[0].service == "mqtt"
    assert disc_list[0].uuid.hex == "889ca604cff84004894e53d181655b3a"
    assert disc_list[0].config["host"] == "core-mosquitto"


async def test_get_discovery(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Discovery get API."""
    uuid = UUID("889ca604cff84004894e53d181655b3a")
    responses.get(
        f"{SUPERVISOR_URL}/discovery/{uuid.hex}",
        status=200,
        body=load_fixture("discovery_get.json"),
    )
    discovery = await supervisor_client.discovery.get(uuid)
    assert discovery.addon == "core_mosquitto"
    assert discovery.service == "mqtt"
    assert discovery.uuid == uuid
    assert discovery.config["host"] == "core-mosquitto"
    assert discovery.config["port"] == 1883
    assert discovery.config["ssl"] is False


async def test_delete_discovery(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Discovery delete API."""
    uuid = UUID("889ca604cff84004894e53d181655b3a")
    responses.delete(f"{SUPERVISOR_URL}/discovery/{uuid.hex}", status=200)
    assert await supervisor_client.discovery.delete(uuid) is None
    assert responses.requests.keys() == {
        ("DELETE", URL(f"{SUPERVISOR_URL}/discovery/{uuid.hex}"))
    }


async def test_set_discovery(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test Discovery set API."""
    responses.post(
        f"{SUPERVISOR_URL}/discovery",
        status=200,
        body=load_fixture("discovery_set.json"),
    )
    assert await supervisor_client.discovery.set(
        DiscoveryConfig(service="mqtt", config={})
    ) == UUID("889ca604cff84004894e53d181655b3a")
