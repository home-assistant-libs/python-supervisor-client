"""Tests for client."""

import pytest

from aiohasupervisor.client import _SupervisorClient
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
