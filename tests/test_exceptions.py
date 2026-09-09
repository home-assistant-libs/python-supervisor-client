"""Tests for error_key to exception class mapping."""

from json import dumps

from aiointercept import aiointercept
import pytest

from aiohasupervisor import SupervisorClient
from aiohasupervisor.exceptions import ERROR_KEYS, SupervisorError

from .const import SUPERVISOR_URL

_SORTED_ERROR_KEYS = sorted(ERROR_KEYS.items())


@pytest.mark.parametrize(
    ("error_key", "exc_type"),
    _SORTED_ERROR_KEYS,
    ids=[key for key, _ in _SORTED_ERROR_KEYS],
)
async def test_error_key_maps_to_exception_type(
    responses: aiointercept,
    supervisor_client: SupervisorClient,
    error_key: str,
    exc_type: type[SupervisorError],
) -> None:
    """Test each registered error_key raises its corresponding exception type."""
    extra_fields = {"some_field": "some_value"}
    message = f"Test message for {error_key}"
    body = dumps(
        {
            "result": "error",
            "message": message,
            "error_key": error_key,
            "extra_fields": extra_fields,
            "job_id": "test-job-id",
        }
    )
    responses.get(f"{SUPERVISOR_URL}/test", status=400, body=body)

    with pytest.raises(exc_type) as exc_info:
        await supervisor_client._client.get("test")

    err = exc_info.value
    assert type(err) is exc_type
    assert err.error_key == error_key
    assert err.extra_fields == extra_fields
    assert err.job_id == "test-job-id"
    assert str(err) == message


@pytest.mark.parametrize(
    ("error_key", "exc_type"),
    _SORTED_ERROR_KEYS,
    ids=[key for key, _ in _SORTED_ERROR_KEYS],
)
def test_error_key_class_attribute_matches_registration(
    error_key: str, exc_type: type[SupervisorError]
) -> None:
    """Test each exception class's error_key attribute matches its registration."""
    assert exc_type.error_key == error_key
    assert issubclass(exc_type, SupervisorError)
