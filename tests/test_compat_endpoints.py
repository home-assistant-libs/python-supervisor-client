"""Test the compat endpoint map stays in sync with the client."""

from collections.abc import Callable
import inspect
import re
import sys
from typing import Any

from aiointercept import aiointercept
import pytest

from aiohasupervisor import SupervisorClient
from aiohasupervisor.client import _SupervisorComponentClient
from aiohasupervisor.exceptions import SupervisorError

from .compat.check_responses import is_omitted, normalize
from .compat.endpoints import ENDPOINTS, Endpoint

if sys.version_info >= (3, 14):
    from annotationlib import Format, get_annotations

# Client methods returning a value without parsing a JSON response
NOT_JSON = {
    "BackupsClient.download_backup",
    "StoreClient.addon_changelog",
    "StoreClient.addon_documentation",
}

PARAM_RE = re.compile(r"\{[^}]*\}")


def placeholder_params(template: str) -> list[str]:
    """Return distinct placeholder params for a template, valid as UUIDs."""
    return [f"{i:032x}" for i in range(1, len(PARAM_RE.findall(template)) + 1)]


def client_classes() -> list[type]:
    """Return the root client and all component client classes."""
    components = [
        inspect.signature(prop.fget).return_annotation
        for prop in vars(SupervisorClient).values()
        if isinstance(prop, property)
    ]
    return [
        SupervisorClient,
        *(cls for cls in components if issubclass(cls, _SupervisorComponentClient)),
    ]


def returns_none(func: Callable[..., Any]) -> bool:
    """Return true if func is annotated to return None.

    Reads the annotation as a string where annotations are evaluated lazily
    (Python 3.14+). Evaluating them in the class scope fails where a method name
    shadows a builtin used in an annotation, like AddonsClient.list.
    """
    if sys.version_info >= (3, 14):
        return get_annotations(func, format=Format.STRING).get("return") == "None"
    return inspect.signature(func).return_annotation is None


def public_methods() -> dict[str, tuple[type, Callable[..., Any]]]:
    """Return public coroutine methods of all clients by qualified name."""
    return {
        f"{cls.__name__}.{name}": (cls, func)
        for cls in client_classes()
        for name, func in vars(cls).items()
        if not name.startswith("_") and inspect.iscoroutinefunction(func)
    }


@pytest.fixture(name="failing_responses")
def failing_responses_fixture(responses: aiointercept) -> aiointercept:
    """Fail every request, so endpoints can be called without a valid response."""
    for method in ("GET", "POST", "PUT", "DELETE"):
        responses.add(
            re.compile(".*"),
            method=method,
            status=500,
            repeat=True,
            content_type="text/plain",
        )
    return responses


@pytest.mark.parametrize(
    "endpoint", ENDPOINTS, ids=[f"{ep.method} {ep.template}" for ep in ENDPOINTS]
)
async def test_endpoint_request(
    failing_responses: aiointercept,
    supervisor_client: SupervisorClient,
    endpoint: Endpoint,
) -> None:
    """Test each endpoint calls the method and path in its template."""
    params = placeholder_params(endpoint.template)

    with pytest.raises(SupervisorError):
        await endpoint.call(supervisor_client, params)

    expected = PARAM_RE.sub(lambda _: params.pop(0), endpoint.template)
    assert [(method, url.path) for method, url in failing_responses.requests] == [
        (endpoint.method, f"/{expected}")
    ]


def test_endpoints_unique() -> None:
    """Test no two endpoints match the same recorded request."""
    keys = [(ep.method, normalize(ep.template)) for ep in ENDPOINTS]
    assert len(keys) == len(set(keys))


def test_endpoints_not_omitted() -> None:
    """Test no endpoint the client implements is also marked omitted."""
    assert [ep.template for ep in ENDPOINTS if is_omitted(ep.template)] == []


@pytest.mark.usefixtures("failing_responses")
async def test_endpoints_cover_client(
    supervisor_client: SupervisorClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test every client method parsing a JSON response has an endpoint."""
    methods = public_methods()
    called: set[str] = set()

    def spy(name: str, func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            called.add(name)
            return await func(*args, **kwargs)

        return wrapper

    for name, (cls, func) in methods.items():
        monkeypatch.setattr(cls, func.__name__, spy(name, func))
    for endpoint in ENDPOINTS:
        params = placeholder_params(endpoint.template)
        with pytest.raises(SupervisorError):
            await endpoint.call(supervisor_client, params)

    returning = {name for name, (_, func) in methods.items() if not returns_none(func)}
    assert returning >= NOT_JSON, "stale NOT_JSON entry"
    assert returning - NOT_JSON - called == set()
