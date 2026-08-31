"""Test NTP supervisor client."""

from aiointercept import aiointercept
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import NTPOptions

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_ntp_info(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test NTP info API."""
    responses.get(
        f"{SUPERVISOR_URL}/ntp/info",
        status=200,
        body=load_fixture("ntp_info.json"),
    )
    info = await supervisor_client.ntp.info()
    assert info.servers == ["time.cloudflare.com"]
    assert info.fallback_servers == ["time.google.com"]


async def test_ntp_set_options(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test NTP set options API."""
    responses.post(f"{SUPERVISOR_URL}/ntp/options", status=200)
    assert (
        await supervisor_client.ntp.set_options(
            NTPOptions(servers=["pool.ntp.org"], fallback_servers=[])
        )
        is None
    )
    assert len(responses.requests) == 1
    assert (
        request := responses.requests[("POST", URL(f"{SUPERVISOR_URL}/ntp/options"))]
    )
    assert request[0].kwargs["json"] == {
        "servers": ["pool.ntp.org"],
        "fallback_servers": [],
    }


async def test_ntp_options_requires_a_field() -> None:
    """Test NTP options rejects an empty payload."""
    with pytest.raises(ValueError, match="At least one field must have a value"):
        NTPOptions()
