"""Tests for aiohasupervisor."""

from pathlib import Path

from aiohttp import ClientTimeout
from yarl import URL

type RequestTimeouts = dict[tuple[str, URL], list[ClientTimeout | None]]


def assert_request_timeout(
    request_timeouts: RequestTimeouts,
    method: str,
    url: str,
    *,
    has_timeout: bool,
) -> None:
    """Assert whether a client side timeout was set for the given request."""
    key = (method, URL(url))
    assert key in request_timeouts, f"no request captured for {key}"
    timeouts = request_timeouts[key]
    assert len(timeouts) == 1, f"expected one request for {key}, got {len(timeouts)}"
    assert bool(timeouts[0]) is has_timeout


def get_fixture_path(filename: str) -> Path:
    """Get fixture path."""
    return Path(__package__) / "fixtures" / filename


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    fixture = get_fixture_path(filename)
    return fixture.read_text(encoding="utf-8")
