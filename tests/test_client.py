"""Tests for client."""

from aiointercept import aiointercept
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.client import _SupervisorClient
from aiohasupervisor.const import ResponseType
from aiohasupervisor.exceptions import SupervisorError

from .const import SUPERVISOR_URL


@pytest.mark.parametrize("method", ["get", "post", "put", "delete"])
async def test_path_manipulation_blocked(method: str) -> None:
    """Test path manipulation prevented."""
    client = _SupervisorClient(SUPERVISOR_URL, "abc123", 10)
    action = getattr(client, method)
    with pytest.raises(SupervisorError):
        # absolute path
        await action("/test/../bad")
    with pytest.raises(SupervisorError):
        # relative path
        await action("test/../bad")
    with pytest.raises(SupervisorError):
        # relative path with percent encoding
        await action("test/%2E%2E/bad")


@pytest.mark.parametrize("method", ["get", "post", "put", "delete"])
@pytest.mark.parametrize(
    ("source", "expected"), [("core.handler", "core.handler"), (None, None)]
)
async def test_source_header(
    responses: aiointercept, method: str, source: str | None, expected: str | None
) -> None:
    """Test X-Hass-Source header only sent when source is set."""
    getattr(responses, method)(f"{SUPERVISOR_URL}/test", status=200)
    async with SupervisorClient(
        SUPERVISOR_URL, "abc123", source=source
    ) as supervisor_client:
        kwargs = {"response_type": ResponseType.NONE} if method == "get" else {}
        await getattr(supervisor_client._client, method)("test", **kwargs)

    request = responses.requests[(method.upper(), URL(f"{SUPERVISOR_URL}/test"))][0]
    assert request.kwargs["headers"].get("X-Hass-Source") == expected
