"""Test Home Assistant supervisor client."""

from ipaddress import IPv4Address
from typing import Any

from aiointercept import aiointercept
import pytest
from yarl import URL

from aiohasupervisor import ResponseLineIterator, SupervisorClient
from aiohasupervisor.models import (
    HomeAssistantOptions,
    HomeAssistantRebuildOptions,
    HomeAssistantRestartOptions,
    HomeAssistantStopOptions,
    HomeAssistantUpdateOptions,
    LogsOptions,
)

from . import RequestTimeouts, assert_request_timeout, load_fixture
from .const import SUPERVISOR_URL


async def test_homeassistant_info(
    responses: aiointercept, supervisor_client: SupervisorClient
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
    assert info.audio_input is None
    assert info.audio_output is None
    assert info.ip_address == IPv4Address("172.30.32.1")


async def test_homeassistant_stats(
    responses: aiointercept, supervisor_client: SupervisorClient
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
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test Home Assistant options API."""
    responses.post(f"{SUPERVISOR_URL}/core/options", status=200)
    assert (
        await supervisor_client.homeassistant.set_options(
            HomeAssistantOptions(watchdog=False, backups_exclude_database=True)
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/core/options"))
    }


@pytest.mark.parametrize("options", [None, HomeAssistantUpdateOptions(backup=False)])
async def test_homeassistant_update(
    responses: aiointercept,
    request_timeouts: RequestTimeouts,
    supervisor_client: SupervisorClient,
    options: HomeAssistantUpdateOptions | None,
) -> None:
    """Test Home Assistant update API."""
    responses.post(f"{SUPERVISOR_URL}/core/update", status=200)
    assert await supervisor_client.homeassistant.update(options) is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/core/update"))}
    assert_request_timeout(
        request_timeouts,
        "POST",
        f"{SUPERVISOR_URL}/core/update",
        has_timeout=False,
    )


@pytest.mark.parametrize("options", [None, HomeAssistantRestartOptions(safe_mode=True)])
async def test_homeassistant_restart(
    responses: aiointercept,
    request_timeouts: RequestTimeouts,
    supervisor_client: SupervisorClient,
    options: HomeAssistantRestartOptions | None,
) -> None:
    """Test Home Assistant restart API."""
    responses.post(f"{SUPERVISOR_URL}/core/restart", status=200)
    assert await supervisor_client.homeassistant.restart(options) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/core/restart"))
    }
    assert_request_timeout(
        request_timeouts,
        "POST",
        f"{SUPERVISOR_URL}/core/restart",
        has_timeout=False,
    )


@pytest.mark.parametrize("options", [None, HomeAssistantStopOptions(force=True)])
async def test_homeassistant_stop(
    responses: aiointercept,
    request_timeouts: RequestTimeouts,
    supervisor_client: SupervisorClient,
    options: HomeAssistantStopOptions | None,
) -> None:
    """Test Home Assistant stop API."""
    responses.post(f"{SUPERVISOR_URL}/core/stop", status=200)
    assert await supervisor_client.homeassistant.stop(options) is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/core/stop"))}
    assert_request_timeout(
        request_timeouts,
        "POST",
        f"{SUPERVISOR_URL}/core/stop",
        has_timeout=False,
    )


async def test_homeassistant_start(
    responses: aiointercept,
    request_timeouts: RequestTimeouts,
    supervisor_client: SupervisorClient,
) -> None:
    """Test Home Assistant start API."""
    responses.post(f"{SUPERVISOR_URL}/core/start", status=200)
    assert await supervisor_client.homeassistant.start() is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/core/start"))}
    assert_request_timeout(
        request_timeouts,
        "POST",
        f"{SUPERVISOR_URL}/core/start",
        has_timeout=False,
    )


async def test_homeassistant_check_config(
    responses: aiointercept,
    request_timeouts: RequestTimeouts,
    supervisor_client: SupervisorClient,
) -> None:
    """Test Home Assistant check config API."""
    responses.post(f"{SUPERVISOR_URL}/core/check", status=200)
    assert await supervisor_client.homeassistant.check_config() is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/core/check"))}
    assert_request_timeout(
        request_timeouts,
        "POST",
        f"{SUPERVISOR_URL}/core/check",
        has_timeout=True,
    )


@pytest.mark.parametrize("options", [None, HomeAssistantRebuildOptions(safe_mode=True)])
async def test_homeassistant_rebuild(
    responses: aiointercept,
    request_timeouts: RequestTimeouts,
    supervisor_client: SupervisorClient,
    options: HomeAssistantRebuildOptions | None,
) -> None:
    """Test Home Assistant rebuild API."""
    responses.post(f"{SUPERVISOR_URL}/core/rebuild", status=200)
    assert await supervisor_client.homeassistant.rebuild(options) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/core/rebuild"))
    }
    assert_request_timeout(
        request_timeouts,
        "POST",
        f"{SUPERVISOR_URL}/core/rebuild",
        has_timeout=False,
    )


@pytest.mark.parametrize(
    ("kwargs", "path"),
    [
        pytest.param({}, "core/logs", id="default"),
        pytest.param({"latest": True}, "core/logs/latest", id="latest"),
        pytest.param({"follow": True}, "core/logs/follow", id="follow"),
        pytest.param({"boot": 0}, "core/logs/boots/0", id="boot"),
        pytest.param(
            {"boot": -1, "follow": True}, "core/logs/boots/-1/follow", id="boot_follow"
        ),
    ],
)
async def test_homeassistant_logs(
    responses: aiointercept,
    supervisor_client: SupervisorClient,
    kwargs: dict[str, Any],
    path: str,
) -> None:
    """Test Home Assistant logs API."""
    responses.get(
        f"{SUPERVISOR_URL}/{path}?lines=10", status=200, body=b"line 1\nline 2\n"
    )
    result = await supervisor_client.homeassistant.logs(LogsOptions(lines=10), **kwargs)
    assert isinstance(result, ResponseLineIterator)
    assert [line async for line in result] == ["line 1", "line 2"]


@pytest.mark.parametrize("kwargs", [{"boot": 0}, {"follow": True}])
async def test_homeassistant_logs_latest_exclusive(
    supervisor_client: SupervisorClient, kwargs: dict[str, Any]
) -> None:
    """Test latest Home Assistant logs can't be combined with a boot or follow."""
    with pytest.raises(ValueError, match="latest can't be combined"):
        await supervisor_client.homeassistant.logs(latest=True, **kwargs)
