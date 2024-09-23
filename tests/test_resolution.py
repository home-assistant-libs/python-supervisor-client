"""Test resolution center supervisor client."""

from uuid import uuid4

from aioresponses import aioresponses
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import CheckOptions

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_resolution_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test resolution center info API."""
    responses.get(
        f"{SUPERVISOR_URL}/resolution/info",
        status=200,
        body=load_fixture("resolution_info.json"),
    )
    info = await supervisor_client.resolution.info()
    assert info.checks[4].enabled is True
    assert info.checks[4].slug == "backups"
    assert info.issues[0].context == "system"
    assert info.issues[0].type == "no_current_backup"
    assert info.issues[0].reference is None
    assert info.issues[0].uuid.hex == "7f0eac2b61c9456dab6970507a276c36"
    assert info.suggestions[0].auto is False
    assert info.suggestions[0].context == "system"
    assert info.suggestions[0].type == "create_full_backup"
    assert info.suggestions[0].reference is None
    assert info.suggestions[0].uuid.hex == "f87d3556f02c4004a47111c072c76fac"
    assert info.unhealthy == ["supervisor"]
    assert info.unsupported == []


async def test_resolution_check_options(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test resolution center check options API."""
    responses.post(f"{SUPERVISOR_URL}/resolution/check/backups/options", status=200)
    assert (
        await supervisor_client.resolution.check_options(
            "backups", CheckOptions(enabled=False)
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/resolution/check/backups/options"))
    }


async def test_resolution_run_check(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test resolution center run check API."""
    responses.post(f"{SUPERVISOR_URL}/resolution/check/backups/run", status=200)
    assert await supervisor_client.resolution.run_check("backups") is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/resolution/check/backups/run"))
    }


async def test_resolution_apply_suggestion(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test resolution center apply suggestion API."""
    uuid = uuid4()
    responses.post(f"{SUPERVISOR_URL}/resolution/suggestion/{uuid.hex}", status=200)
    assert await supervisor_client.resolution.apply_suggestion(uuid) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/resolution/suggestion/{uuid.hex}"))
    }


async def test_resolution_dismiss_suggestion(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test resolution center dismiss suggestion API."""
    uuid = uuid4()
    responses.delete(f"{SUPERVISOR_URL}/resolution/suggestion/{uuid.hex}", status=200)
    assert await supervisor_client.resolution.dismiss_suggestion(uuid) is None
    assert responses.requests.keys() == {
        ("DELETE", URL(f"{SUPERVISOR_URL}/resolution/suggestion/{uuid.hex}"))
    }


async def test_resolution_dismiss_issue(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test resolution center dismiss issue API."""
    uuid = uuid4()
    responses.delete(f"{SUPERVISOR_URL}/resolution/issue/{uuid.hex}", status=200)
    assert await supervisor_client.resolution.dismiss_issue(uuid) is None
    assert responses.requests.keys() == {
        ("DELETE", URL(f"{SUPERVISOR_URL}/resolution/issue/{uuid.hex}"))
    }


async def test_resolution_suggestions_for_issue(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test resolution center suggestions for issue API."""
    uuid = uuid4()
    responses.get(
        f"{SUPERVISOR_URL}/resolution/issue/{uuid.hex}/suggestions",
        status=200,
        body=load_fixture("resolution_suggestions_for_issue.json"),
    )
    result = await supervisor_client.resolution.suggestions_for_issue(uuid)
    assert result[0].auto is False
    assert result[0].context == "system"
    assert result[0].type == "create_full_backup"


async def test_resolution_healthcheck(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test resolution center healthcheck API."""
    responses.post(f"{SUPERVISOR_URL}/resolution/healthcheck", status=200)
    assert await supervisor_client.resolution.healthcheck() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/resolution/healthcheck"))
    }
