"""Test for supervisor management client."""

from ipaddress import IPv4Address
import json
from typing import Any

from aiointercept import aiointercept
import pytest
from yarl import URL

from aiohasupervisor import ResponseLineIterator, SupervisorClient
from aiohasupervisor.models import (
    LogsOptions,
    SupervisorOptions,
    SupervisorUpdateOptions,
)
from aiohasupervisor.models.supervisor import DetectBlockingIO, FeatureFlag

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_supervisor_ping(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor ping API."""
    responses.get(f"{SUPERVISOR_URL}/supervisor/ping", status=200)
    assert await supervisor_client.supervisor.ping() is None
    assert responses.requests.keys() == {
        ("GET", URL(f"{SUPERVISOR_URL}/supervisor/ping"))
    }


async def test_supervisor_info(
    responses: aiointercept, supervisor_client: SupervisorClient
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
    assert info.country is None
    assert info.detect_blocking_io is False
    assert info.feature_flags == {FeatureFlag.SUPERVISOR_V2_API: False}


@pytest.mark.parametrize("field", ["version_latest", "arch"])
async def test_supervisor_info_optional_fields_none(
    responses: aiointercept,
    supervisor_client: SupervisorClient,
    field: str,
) -> None:
    """Test supervisor info API when optional fields are None."""
    fixture = json.loads(load_fixture("supervisor_info.json"))
    fixture["data"][field] = None
    responses.get(
        f"{SUPERVISOR_URL}/supervisor/info",
        status=200,
        payload=fixture,
    )
    info = await supervisor_client.supervisor.info()
    assert getattr(info, field) is None


async def test_supervisor_stats(
    responses: aiointercept, supervisor_client: SupervisorClient
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
    responses: aiointercept,
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
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor reload API."""
    responses.post(f"{SUPERVISOR_URL}/supervisor/reload", status=200)
    assert await supervisor_client.supervisor.reload() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/supervisor/reload"))
    }


async def test_supervisor_restart(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor restart API."""
    responses.post(f"{SUPERVISOR_URL}/supervisor/restart", status=200)
    assert await supervisor_client.supervisor.restart() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/supervisor/restart"))
    }


async def test_supervisor_options(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor options API."""
    responses.post(f"{SUPERVISOR_URL}/supervisor/options", status=200)
    assert (
        await supervisor_client.supervisor.set_options(
            SupervisorOptions(
                debug=True,
                debug_block=True,
                country="NL",
                detect_blocking_io=DetectBlockingIO.ON_AT_STARTUP,
            )
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/supervisor/options"))
    }
    assert (
        request := responses.requests[
            ("POST", URL(f"{SUPERVISOR_URL}/supervisor/options"))
        ]
    )
    assert request[0].kwargs["json"] == {
        "debug": True,
        "debug_block": True,
        "country": "NL",
        "detect_blocking_io": "on_at_startup",
    }


async def test_supervisor_info_unknown_feature_flag(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor info with an unknown feature flag returns it as a string key."""
    fixture = json.loads(load_fixture("supervisor_info.json"))
    fixture["data"]["feature_flags"]["future_feature"] = True
    responses.get(
        f"{SUPERVISOR_URL}/supervisor/info",
        status=200,
        payload=fixture,
    )
    info = await supervisor_client.supervisor.info()
    assert info.feature_flags[FeatureFlag.SUPERVISOR_V2_API] is False
    assert info.feature_flags["future_feature"] is True


async def test_supervisor_options_feature_flags(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor options API with feature_flags."""
    responses.post(f"{SUPERVISOR_URL}/supervisor/options", status=200)
    assert (
        await supervisor_client.supervisor.set_options(
            SupervisorOptions(
                feature_flags={FeatureFlag.SUPERVISOR_V2_API: True},
            )
        )
        is None
    )
    assert (
        request := responses.requests[
            ("POST", URL(f"{SUPERVISOR_URL}/supervisor/options"))
        ]
    )
    assert request[0].kwargs["json"] == {
        "feature_flags": {"supervisor_v2_api": True},
    }


async def test_supervisor_repair(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test supervisor repair API."""
    responses.post(f"{SUPERVISOR_URL}/supervisor/repair", status=200)
    assert await supervisor_client.supervisor.repair() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/supervisor/repair"))
    }


@pytest.mark.parametrize(
    ("kwargs", "path"),
    [
        pytest.param({}, "supervisor/logs", id="default"),
        pytest.param({"latest": True}, "supervisor/logs/latest", id="latest"),
        pytest.param({"follow": True}, "supervisor/logs/follow", id="follow"),
        pytest.param({"boot": 0}, "supervisor/logs/boots/0", id="boot"),
        pytest.param(
            {"boot": -1, "follow": True},
            "supervisor/logs/boots/-1/follow",
            id="boot_follow",
        ),
    ],
)
async def test_supervisor_logs(
    responses: aiointercept,
    supervisor_client: SupervisorClient,
    kwargs: dict[str, Any],
    path: str,
) -> None:
    """Test supervisor logs API."""
    responses.get(
        f"{SUPERVISOR_URL}/{path}?lines=10", status=200, body=b"line 1\nline 2\n"
    )
    result = await supervisor_client.supervisor.logs(LogsOptions(lines=10), **kwargs)
    assert isinstance(result, ResponseLineIterator)
    assert [line async for line in result] == ["line 1", "line 2"]


@pytest.mark.parametrize("kwargs", [{"boot": 0}, {"follow": True}])
async def test_supervisor_logs_latest_exclusive(
    supervisor_client: SupervisorClient, kwargs: dict[str, Any]
) -> None:
    """Test latest supervisor logs can't be combined with a boot or follow."""
    with pytest.raises(ValueError, match="latest can't be combined"):
        await supervisor_client.supervisor.logs(latest=True, **kwargs)
