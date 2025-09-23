"""Tests for store supervisor client."""

from json import loads

from aioresponses import aioresponses
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.exceptions import (
    AddonNotSupportedArchitectureError,
    AddonNotSupportedHomeAssistantVersionError,
    AddonNotSupportedMachineTypeError,
    SupervisorBadRequestError,
    SupervisorError,
)
from aiohasupervisor.models import StoreAddonUpdate, StoreAddRepository
from aiohasupervisor.models.addons import StoreAddonInstall

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_store_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store info API."""
    responses.get(
        f"{SUPERVISOR_URL}/store", status=200, body=load_fixture("store_info.json")
    )
    store = await supervisor_client.store.info()

    assert len(store.repositories) == 6
    assert store.repositories[0].slug == "local"
    assert store.repositories[0].name == "Local add-ons"

    assert len(store.addons) == 88
    assert store.addons[0].slug == "d5369777_music_assistant"
    assert store.addons[0].name == "Music Assistant Server"


async def test_store_addons_list(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store addons list API."""
    responses.get(
        f"{SUPERVISOR_URL}/store/addons",
        status=200,
        body=load_fixture("store_addons_list.json"),
    )
    addons = await supervisor_client.store.addons_list()

    assert len(addons) == 88
    assert addons[0].slug == "d5369777_music_assistant"
    assert addons[0].name == "Music Assistant Server"


async def test_store_repositories_list(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store repositories list API."""
    responses.get(
        f"{SUPERVISOR_URL}/store/repositories",
        status=200,
        body=load_fixture("store_repositories_list.json"),
    )
    repositories = await supervisor_client.store.repositories_list()

    assert len(repositories) == 6
    assert repositories[0].slug == "local"
    assert repositories[0].name == "Local add-ons"


async def test_store_addon_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store addon info API."""
    responses.get(
        f"{SUPERVISOR_URL}/store/addons/core_mosquitto",
        status=200,
        body=load_fixture("store_addon_info.json"),
    )
    info = await supervisor_client.store.addon_info("core_mosquitto")

    assert info.name == "Mosquitto broker"
    assert info.slug == "core_mosquitto"
    assert info.signed is True
    assert info.supervisor_api is False
    assert info.supervisor_role == "default"


async def test_store_addon_changelog(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store addon info changelog API."""
    responses.get(
        f"{SUPERVISOR_URL}/store/addons/core_mosquitto/changelog",
        status=200,
        body=load_fixture("store_addon_changelog.txt"),
    )
    changelog = await supervisor_client.store.addon_changelog("core_mosquitto")
    assert changelog.startswith("# Changelog")


async def test_store_addon_documentation(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store addon documentation API."""
    responses.get(
        f"{SUPERVISOR_URL}/store/addons/core_mosquitto/documentation",
        status=200,
        body=load_fixture("store_addon_documentation.txt"),
    )
    documentation = await supervisor_client.store.addon_documentation("core_mosquitto")
    assert documentation.startswith("# Home Assistant Add-on: Mosquitto broker")


@pytest.mark.parametrize(
    ("options", "has_timeout"),
    [
        (None, False),
        (StoreAddonInstall(), False),
        (StoreAddonInstall(background=False), False),
        (StoreAddonInstall(background=True), True),
    ],
)
async def test_store_addon_install(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: StoreAddonInstall | None,
    has_timeout: bool,  # noqa: FBT001
) -> None:
    """Test store addon install API."""
    responses.post(f"{SUPERVISOR_URL}/store/addons/core_mosquitto/install", status=200)

    assert (
        await supervisor_client.store.install_addon("core_mosquitto", options)
    ) is None
    assert (
        bool(
            responses.requests[
                ("POST", URL(f"{SUPERVISOR_URL}/store/addons/core_mosquitto/install"))
            ][0].kwargs["timeout"]
        )
        is has_timeout
    )


@pytest.mark.parametrize(
    ("options", "has_timeout"),
    [
        (None, False),
        (StoreAddonUpdate(), False),
        (StoreAddonUpdate(backup=True), False),
        (StoreAddonUpdate(background=False), False),
        (StoreAddonUpdate(background=True), True),
    ],
)
async def test_store_addon_update(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: StoreAddonUpdate | None,
    has_timeout: bool,  # noqa: FBT001
) -> None:
    """Test store addon update API."""
    responses.post(f"{SUPERVISOR_URL}/store/addons/core_mosquitto/update", status=200)

    assert (
        await supervisor_client.store.update_addon("core_mosquitto", options)
    ) is None
    assert (
        bool(
            responses.requests[
                ("POST", URL(f"{SUPERVISOR_URL}/store/addons/core_mosquitto/update"))
            ][0].kwargs["timeout"]
        )
        is has_timeout
    )


async def test_store_addon_availability(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store addon availability API."""
    responses.get(
        f"{SUPERVISOR_URL}/store/addons/core_mosquitto/availability", status=200
    )

    assert (await supervisor_client.store.addon_availability("core_mosquitto")) is None


@pytest.mark.parametrize(
    ("error_fixture", "error_key", "exc_type"),
    [
        (
            "store_addon_availability_error_architecture.json",
            "addon_not_supported_architecture_error",
            AddonNotSupportedArchitectureError,
        ),
        (
            "store_addon_availability_error_machine.json",
            "addon_not_supported_machine_type_error",
            AddonNotSupportedMachineTypeError,
        ),
        (
            "store_addon_availability_error_home_assistant.json",
            "addon_not_supported_home_assistant_version_error",
            AddonNotSupportedHomeAssistantVersionError,
        ),
        (
            "store_addon_availability_error_other.json",
            None,
            SupervisorBadRequestError,
        ),
    ],
)
async def test_store_addon_availability_error(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    error_fixture: str,
    error_key: str | None,
    exc_type: type[SupervisorError],
) -> None:
    """Test store addon availability errors."""
    error_body = load_fixture(error_fixture)
    error_data = loads(error_body)

    def check_availability_error(err: SupervisorError) -> bool:
        assert err.error_key == error_key
        assert err.extra_fields == error_data["extra_fields"]
        return True

    # Availability API
    responses.get(
        f"{SUPERVISOR_URL}/store/addons/core_mosquitto/availability",
        status=400,
        body=error_body,
    )
    with pytest.raises(
        exc_type, match=error_data["message"], check=check_availability_error
    ):
        await supervisor_client.store.addon_availability("core_mosquitto")

    # Install API
    responses.post(
        f"{SUPERVISOR_URL}/store/addons/core_mosquitto/install",
        status=400,
        body=error_body,
    )
    with pytest.raises(
        exc_type, match=error_data["message"], check=check_availability_error
    ):
        await supervisor_client.store.install_addon("core_mosquitto")

    # Update API
    responses.post(
        f"{SUPERVISOR_URL}/store/addons/core_mosquitto/update",
        status=400,
        body=error_body,
    )
    with pytest.raises(
        exc_type, match=error_data["message"], check=check_availability_error
    ):
        await supervisor_client.store.update_addon("core_mosquitto")


async def test_store_reload(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store reload API."""
    responses.post(f"{SUPERVISOR_URL}/store/reload", status=200)

    assert (await supervisor_client.store.reload()) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/store/reload"))
    }


async def test_store_repository_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store repository info API."""
    responses.get(
        f"{SUPERVISOR_URL}/store/repositories/core",
        status=200,
        body=load_fixture("store_repository_info.json"),
    )
    repository = await supervisor_client.store.repository_info("core")
    assert repository.slug == "core"
    assert repository.name == "Official add-ons"
    assert repository.source == "core"


async def test_store_add_repository(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store add repository API."""
    responses.post(f"{SUPERVISOR_URL}/store/repositories", status=200)

    assert (
        await supervisor_client.store.add_repository(
            StoreAddRepository(repository="test")
        )
    ) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/store/repositories"))
    }


async def test_store_remove_repository(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store addon info API."""
    responses.delete(f"{SUPERVISOR_URL}/store/repositories/test", status=200)

    assert (await supervisor_client.store.remove_repository("test")) is None
    assert responses.requests.keys() == {
        ("DELETE", URL(f"{SUPERVISOR_URL}/store/repositories/test"))
    }
