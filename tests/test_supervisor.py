"""Test for supervisor management client."""

from ipaddress import IPv4Address

from aioresponses import aioresponses
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import SupervisorOptions, SupervisorUpdateOptions

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_supervisor_ping(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor ping API."""
    responses.get(f"{SUPERVISOR_URL}/supervisor/ping", status=200)
    assert await supervisor_client.supervisor.ping() is None
    assert responses.requests.keys() == {
        ("GET", URL(f"{SUPERVISOR_URL}/supervisor/ping"))
    }


async def test_supervisor_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor info API."""
    responses.get(
        f"{SUPERVISOR_URL}/supervisor/info",
        status=200,
        body=load_fixture("supervisor_info.json"),
    )
    info = await supervisor_client.supervisor.info()

    assert info.version == "2024.09.1"
    assert info.channel == "stable"
    assert info.arch == "aarch64"
    assert info.supported is True
    assert info.healthy is True
    assert info.logging == "info"
    assert info.ip_address == IPv4Address("172.30.32.2")


async def test_supervisor_stats(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor stats API."""
    responses.get(
        f"{SUPERVISOR_URL}/supervisor/stats",
        status=200,
        body=load_fixture("supervisor_stats.json"),
    )
    stats = await supervisor_client.supervisor.stats()

    assert stats.cpu_percent == 0.04
    assert stats.memory_usage == 243982336
    assert stats.memory_limit == 3899138048
    assert stats.memory_percent == 6.26


@pytest.mark.parametrize(
    "options", [None, SupervisorUpdateOptions(version="2024.01.0")]
)
async def test_supervisor_update(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: SupervisorUpdateOptions | None,
) -> None:
    """Test supervisor update API."""
    responses.post(f"{SUPERVISOR_URL}/supervisor/update", status=200)
    assert await supervisor_client.supervisor.update(options) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/supervisor/update"))
    }


async def test_supervisor_reload(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor reload API."""
    responses.post(f"{SUPERVISOR_URL}/supervisor/reload", status=200)
    assert await supervisor_client.supervisor.reload() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/supervisor/reload"))
    }


async def test_supervisor_restart(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor restart API."""
    responses.post(f"{SUPERVISOR_URL}/supervisor/restart", status=200)
    assert await supervisor_client.supervisor.restart() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/supervisor/restart"))
    }


async def test_supervisor_options(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor options API."""
    responses.post(f"{SUPERVISOR_URL}/supervisor/options", status=200)
    assert (
        await supervisor_client.supervisor.options(
            SupervisorOptions(debug=True, debug_block=True)
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/supervisor/options"))
    }


async def test_supervisor_repair(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor repair API."""
    responses.post(f"{SUPERVISOR_URL}/supervisor/repair", status=200)
    assert await supervisor_client.supervisor.repair() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/supervisor/repair"))
    }
