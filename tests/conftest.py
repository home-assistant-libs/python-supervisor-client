"""Shared fixtures for aiohasupervisor tests."""

from collections.abc import AsyncGenerator
from typing import Any

from aiohttp import ClientSession
from aiointercept import aiointercept
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient

from . import RequestTimeouts
from .const import SUPERVISOR_URL


@pytest.fixture(name="supervisor_client")
async def client() -> AsyncGenerator[SupervisorClient, None]:
    """Return a Supervisor client."""
    async with SupervisorClient(
        SUPERVISOR_URL,
        "abc123",
    ) as supervisor_client:
        yield supervisor_client


@pytest.fixture(name="responses")
async def aiointercept_fixture() -> AsyncGenerator[aiointercept, None]:
    """Return aiointercept fixture."""
    async with aiointercept(mock_external_urls=True) as mocked_responses:
        yield mocked_responses


@pytest.fixture(name="request_timeouts")
def request_timeouts_fixture(monkeypatch: pytest.MonkeyPatch) -> RequestTimeouts:
    """Capture the client side timeout passed to each request.

    aiointercept routes requests through a real test server, so the client side
    timeout is not visible in the captured request. Record it here instead.
    """
    timeouts: RequestTimeouts = {}
    original = ClientSession.request

    def _capture(
        self: ClientSession, method: str, str_or_url: Any, **kwargs: Any
    ) -> Any:
        key = (method, URL(str_or_url))
        timeouts.setdefault(key, []).append(kwargs.get("timeout"))
        return original(self, method, str_or_url, **kwargs)

    monkeypatch.setattr(ClientSession, "request", _capture)
    return timeouts
