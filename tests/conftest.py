"""Shared fixtures for aiohasupervisor tests."""

from collections.abc import AsyncGenerator, Generator

from aioresponses import aioresponses
import pytest

from aiohasupervisor import SupervisorClient

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
def aioresponses_fixture() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses
