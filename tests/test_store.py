"""Tests for store supervisor client."""

from aioresponses import aioresponses
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import StoreAddonUpdate, StoreAddRepository

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


async def test_store_addon_install(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store addon install API."""
    responses.post(f"{SUPERVISOR_URL}/store/addons/core_mosquitto/install", status=200)

    assert (await supervisor_client.store.install_addon("core_mosquitto")) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/store/addons/core_mosquitto/install"))
    }


async def test_store_addon_update(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test store addon update API."""
    responses.post(f"{SUPERVISOR_URL}/store/addons/core_mosquitto/update", status=200)

    assert (
        await supervisor_client.store.update_addon(
            "core_mosquitto", StoreAddonUpdate(backup=True)
        )
    ) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/store/addons/core_mosquitto/update"))
    }


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
