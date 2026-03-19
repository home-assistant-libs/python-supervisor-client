"""Test ingress component client."""

from aioresponses import aioresponses
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import CreateSessionOptions

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_panels(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test panels API."""
    responses.get(
        f"{SUPERVISOR_URL}/ingress/panels",
        status=200,
        body=load_fixture("ingress_panels.json"),
    )
    result = await supervisor_client.ingress.panels()
    assert "core_ssh" in result
    assert result["core_ssh"].title == "Terminal"
    assert result["core_ssh"].icon == "mdi:console"
    assert result["core_ssh"].admin is True
    assert result["core_ssh"].enable is False
    assert "a0d7b954_vscode" in result
    assert result["a0d7b954_vscode"].title == "Studio Code Server"
    assert result["a0d7b954_vscode"].icon == "mdi:microsoft-visual-studio-code"
    assert result["a0d7b954_vscode"].admin is True
    assert result["a0d7b954_vscode"].enable is True


@pytest.mark.parametrize(
    ("options", "expected_body"),
    [(None, None), (CreateSessionOptions(user_id="test"), {"user_id": "test"})],
)
async def test_create_session(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: CreateSessionOptions | None,
    expected_body: dict[str, str] | None,
) -> None:
    """Test create session API."""
    session_url = f"{SUPERVISOR_URL}/ingress/session"
    responses.post(session_url, status=200, body=load_fixture("create_session.json"))
    result = await supervisor_client.ingress.create_session(options)
    assert result == "abc123"

    assert responses.requests.keys() == {("POST", URL(session_url))}
    session_calls = responses.requests[("POST", URL(session_url))]
    assert len(session_calls) == 1
    assert session_calls[0].kwargs["json"] == expected_body


async def test_validate_session(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test validate session API."""
    validate_url = f"{SUPERVISOR_URL}/ingress/validate_session"
    responses.post(validate_url, status=200)
    assert await supervisor_client.ingress.validate_session("abc123") is None

    assert responses.requests.keys() == {("POST", URL(validate_url))}
    validate_calls = responses.requests[("POST", URL(validate_url))]
    assert len(validate_calls) == 1
    assert validate_calls[0].kwargs["json"] == {"session": "abc123"}
