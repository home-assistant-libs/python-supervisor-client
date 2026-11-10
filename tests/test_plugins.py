"""Test plugins supervisor client."""

from typing import Any

from aiointercept import aiointercept
import pytest

from aiohasupervisor import ResponseLineIterator, SupervisorClient
from aiohasupervisor.models import LogsOptions, Plugin

from .const import SUPERVISOR_URL


@pytest.mark.parametrize(
    ("plugin", "kwargs", "path"),
    [
        pytest.param(Plugin.DNS, {}, "dns/logs", id="default"),
        pytest.param(Plugin.AUDIO, {"latest": True}, "audio/logs/latest", id="latest"),
        pytest.param(Plugin.CLI, {"follow": True}, "cli/logs/follow", id="follow"),
        pytest.param(
            Plugin.MULTICAST, {"boot": 0}, "multicast/logs/boots/0", id="boot"
        ),
        pytest.param(
            Plugin.OBSERVER,
            {"boot": -1, "follow": True},
            "observer/logs/boots/-1/follow",
            id="boot_follow",
        ),
    ],
)
async def test_plugin_logs(
    responses: aiointercept,
    supervisor_client: SupervisorClient,
    plugin: Plugin,
    kwargs: dict[str, Any],
    path: str,
) -> None:
    """Test plugin logs API."""
    responses.get(
        f"{SUPERVISOR_URL}/{path}?lines=10", status=200, body=b"line 1\nline 2\n"
    )
    result = await supervisor_client.plugins.logs(
        plugin, LogsOptions(lines=10), **kwargs
    )
    assert isinstance(result, ResponseLineIterator)
    assert [line async for line in result] == ["line 1", "line 2"]


@pytest.mark.parametrize("kwargs", [{"boot": 0}, {"follow": True}])
async def test_plugin_logs_latest_exclusive(
    supervisor_client: SupervisorClient, kwargs: dict[str, Any]
) -> None:
    """Test latest plugin logs can't be combined with a boot or follow."""
    with pytest.raises(ValueError, match="latest can't be combined"):
        await supervisor_client.plugins.logs(Plugin.DNS, latest=True, **kwargs)
