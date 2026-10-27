"""Tests for client."""

from collections.abc import AsyncGenerator
from pathlib import Path
import shutil
import tempfile

from aiohttp import ClientSession, TCPConnector, UnixConnector, web
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


async def test_unread_body_releases_connection(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test a large body which is not read does not leak its connection."""
    responses.post(
        f"{SUPERVISOR_URL}/supervisor/reload",
        status=200,
        body=b"x" * (2 * 1024 * 1024),
    )
    await supervisor_client.supervisor.reload()
    # TCPConnector._acquired is an aiohttp internal holding in-use connections
    assert not supervisor_client._client.session.connector._acquired


@pytest.fixture(name="unix_socket_server")
async def unix_socket_server_fixture() -> (
    AsyncGenerator[tuple[Path, list[web.Request]], None]
):
    """Serve Supervisor's ping on a Unix socket and record requests made to it."""
    requests: list[web.Request] = []

    async def ping(request: web.Request) -> web.Response:
        requests.append(request)
        return web.json_response({"result": "ok", "data": {}})

    app = web.Application()
    app.router.add_get("/supervisor/ping", ping)
    runner = web.AppRunner(app)
    await runner.setup()
    # Not tmp_path, it exceeds the sun_path limit on macOS (104 bytes)
    socket_dir = tempfile.mkdtemp(dir="/tmp")
    path = Path(socket_dir, "supervisor.sock")
    await web.UnixSite(runner, str(path)).start()
    yield path, requests
    await runner.cleanup()
    shutil.rmtree(socket_dir)


async def test_unix_socket(unix_socket_server: tuple[Path, list[web.Request]]) -> None:
    """Test client connects over a Unix socket and sends no token there."""
    path, requests = unix_socket_server
    async with SupervisorClient(unix_socket=path) as supervisor_client:
        await supervisor_client.supervisor.ping()
        connector = supervisor_client._client.session.connector
        assert isinstance(connector, UnixConnector)
        assert connector.path == str(path)

    assert len(requests) == 1
    assert requests[0].host == "localhost"
    assert "Authorization" not in requests[0].headers


async def test_unix_socket_with_session(
    unix_socket_server: tuple[Path, list[web.Request]],
) -> None:
    """Test a passed session is used for a Unix socket and left open."""
    path, requests = unix_socket_server
    async with ClientSession(connector=UnixConnector(path=str(path))) as session:
        async with SupervisorClient(
            session=session, unix_socket=path
        ) as supervisor_client:
            await supervisor_client.supervisor.ping()
            assert supervisor_client._client.session is session

        assert not session.closed

    assert len(requests) == 1
    assert "Authorization" not in requests[0].headers


async def test_tcp_sends_token(responses: aiointercept) -> None:
    """Test client connects over TCP and sends the token without a Unix socket."""
    responses.get(f"{SUPERVISOR_URL}/supervisor/ping", status=200)
    async with SupervisorClient(SUPERVISOR_URL, "abc123") as supervisor_client:
        await supervisor_client.supervisor.ping()
        assert isinstance(supervisor_client._client.session.connector, TCPConnector)

    request = responses.requests[("GET", URL(f"{SUPERVISOR_URL}/supervisor/ping"))][0]
    assert request.kwargs["headers"]["Authorization"] == "Bearer abc123"


@pytest.mark.parametrize(
    ("api_host", "token"), [(None, "abc123"), (SUPERVISOR_URL, None), (None, None)]
)
def test_tcp_requires_api_host_and_token(
    api_host: str | None, token: str | None
) -> None:
    """Test api_host and token are required without a Unix socket."""
    with pytest.raises(ValueError, match="api_host and token are required"):
        SupervisorClient(api_host, token)


def test_unix_socket_rejects_token() -> None:
    """Test a token cannot be passed with a Unix socket."""
    with pytest.raises(ValueError, match="token cannot be used with unix_socket"):
        SupervisorClient(None, "abc123", unix_socket=Path("/run/supervisor.sock"))
