"""Test root services on supervisor client."""

from json import dumps

from aiohttp import ClientSession
from aioresponses import aioresponses
import pytest
from yarl import URL

from aiohasupervisor import (
    SupervisorAuthenticationError,
    SupervisorBadRequestError,
    SupervisorClient,
    SupervisorError,
    SupervisorForbiddenError,
    SupervisorNotFoundError,
    SupervisorServiceUnavailableError,
)
from aiohasupervisor.models import HostFeature, SupervisorState, UpdateType

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_using_own_session(responses: aioresponses) -> None:
    """Test passing in an existing session."""
    responses.get(
        f"{SUPERVISOR_URL}/info", status=200, body=load_fixture("root_info.json")
    )
    async with ClientSession() as session:
        client = SupervisorClient(SUPERVISOR_URL, "abc123", session=session)
        info = await client.info()
        assert info
        assert client._client.session == session
        assert not session.closed
        await client.close()
        assert not session.closed


async def test_using_new_session(responses: aioresponses) -> None:
    """Test letting client create new session."""
    responses.get(
        f"{SUPERVISOR_URL}/info", status=200, body=load_fixture("root_info.json")
    )
    async with SupervisorClient(SUPERVISOR_URL, "abc123") as client:
        info = await client.info()
        assert info
        assert client._client.session
        assert not client._client.session.closed

    assert client._client.session.closed


async def test_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test info API."""
    responses.get(
        f"{SUPERVISOR_URL}/info", status=200, body=load_fixture("root_info.json")
    )
    info = await supervisor_client.info()
    assert info.supervisor == "2024.07.1.dev3001"
    assert info.homeassistant == "2024.6.0.dev202405280218"
    assert info.hassos == "12.4.dev20240527"
    assert info.hostname == "homeassistant"
    assert info.arch == "aarch64"
    assert info.supported is True
    assert info.state == SupervisorState.RUNNING
    assert HostFeature.REBOOT in info.features
    assert "not_real" in info.features


async def test_available_updates(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test available updates API."""
    responses.get(
        f"{SUPERVISOR_URL}/available_updates",
        status=200,
        body=load_fixture("root_available_updates.json"),
    )
    updates = await supervisor_client.available_updates()
    assert updates[0].update_type == UpdateType.CORE
    assert updates[0].panel_path == "/update-available/core"
    assert updates[0].version_latest == "2024.9.0.dev202408010224"
    assert updates[0].name is None
    assert updates[0].icon is None
    assert updates[1].update_type == UpdateType.OS


async def test_refresh_updates(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test refresh updates API."""
    responses.post(f"{SUPERVISOR_URL}/refresh_updates", status=200)
    assert await supervisor_client.refresh_updates() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/refresh_updates"))
    }


@pytest.mark.parametrize(
    ("status", "message", "expected_exc"),
    [
        (400, "Bad input", SupervisorBadRequestError),
        (401, None, SupervisorAuthenticationError),
        (403, "Not allowed", SupervisorForbiddenError),
        (404, "Not found", SupervisorNotFoundError),
        (503, "DB migration in progress", SupervisorServiceUnavailableError),
        (500, "Unknown error", SupervisorError),
    ],
)
async def test_error_handling(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    status: int,
    message: str | None,
    expected_exc: type[SupervisorError],
) -> None:
    """Test error handling scenarios."""
    if message is not None:
        kwargs = {
            "body": dumps(
                {
                    "result": "error",
                    "message": message,
                }
            )
        }
    else:
        kwargs = {"content_type": "text/plain"}

    responses.post(f"{SUPERVISOR_URL}/refresh_updates", status=status, **kwargs)

    with pytest.raises(expected_exc, match=message):
        await supervisor_client.refresh_updates()
