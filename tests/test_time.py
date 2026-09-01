"""Test time supervisor client."""

from aiointercept import aiointercept
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import TimeOptions

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_time_info(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test time info API."""
    responses.get(
        f"{SUPERVISOR_URL}/time/info",
        status=200,
        body=load_fixture("time_info.json"),
    )
    info = await supervisor_client.time.info()
    assert info.config.servers == ["time.cloudflare.com"]
    assert info.config.fallback_servers == ["time.google.com"]


async def test_time_set_options(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test time set options API."""
    responses.post(f"{SUPERVISOR_URL}/time/options", status=200)
    assert (
        await supervisor_client.time.set_options(
            TimeOptions(servers=["pool.ntp.org"], fallback_servers=[])
        )
        is None
    )
    assert len(responses.requests) == 1
    assert (
        request := responses.requests[("POST", URL(f"{SUPERVISOR_URL}/time/options"))]
    )
    assert request[0].kwargs["json"] == {
        "servers": ["pool.ntp.org"],
        "fallback_servers": [],
    }


async def test_time_options_requires_a_field() -> None:
    """Test time options rejects an empty payload."""
    with pytest.raises(ValueError, match="At least one field must have a value"):
        TimeOptions()
