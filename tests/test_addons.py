"""Test addons supervisor client."""

from ipaddress import IPv4Address

from aioresponses import aioresponses
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import (
    AddonBoot,
    AddonsOptions,
    AddonsSecurityOptions,
    AddonStage,
    AddonState,
    AddonsUninstall,
    Capability,
    InstalledAddonComplete,
    StoreAddonComplete,
    SupervisorRole,
)
from aiohasupervisor.models.base import Response

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_addons_list(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test addons list API."""
    responses.get(
        f"{SUPERVISOR_URL}/addons", status=200, body=load_fixture("addons_list.json")
    )
    addons = await supervisor_client.addons.list()
    assert addons[0].name == "Terminal & SSH"
    assert addons[0].slug == "core_ssh"
    assert addons[0].icon is True
    assert addons[0].logo is True
    assert addons[0].state == AddonState.STARTED
    assert addons[0].stage == AddonStage.STABLE
    assert addons[1].slug == "a0d7b954_vscode"


async def test_addons_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test addons info API."""
    responses.get(
        f"{SUPERVISOR_URL}/addons/core_ssh/info",
        status=200,
        body=load_fixture("addons_info.json"),
    )
    addon = await supervisor_client.addons.addon_info("core_ssh")
    assert addon.name == "Terminal & SSH"
    assert addon.slug == "core_ssh"
    assert addon.documentation is True
    assert addon.changelog is True
    assert addon.watchdog is False
    assert addon.auto_update is False
    assert addon.ip_address == IPv4Address("172.30.33.0")
    assert Capability.NET_RAW in addon.privileged
    assert "not_real" in addon.privileged
    assert addon.supervisor_api is True
    assert addon.supervisor_role == SupervisorRole.MANAGER


async def test_addons_uninstall(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test uninstall addon API."""
    responses.post(f"{SUPERVISOR_URL}/addons/core_ssh/uninstall", status=200)
    assert (
        await supervisor_client.addons.uninstall_addon(
            "core_ssh", AddonsUninstall(remove_config=True)
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/addons/core_ssh/uninstall"))
    }


async def test_addons_start(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test start addon API."""
    responses.post(f"{SUPERVISOR_URL}/addons/core_ssh/start", status=200)
    assert await supervisor_client.addons.start_addon("core_ssh") is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/addons/core_ssh/start"))
    }


async def test_addons_stop(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test stop addon API."""
    responses.post(f"{SUPERVISOR_URL}/addons/core_ssh/stop", status=200)
    assert await supervisor_client.addons.stop_addon("core_ssh") is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/addons/core_ssh/stop"))
    }


async def test_addons_restart(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test restart addon API."""
    responses.post(f"{SUPERVISOR_URL}/addons/core_ssh/restart", status=200)
    assert await supervisor_client.addons.restart_addon("core_ssh") is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/addons/core_ssh/restart"))
    }


async def test_addons_options(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test addon options API."""
    responses.post(f"{SUPERVISOR_URL}/addons/core_ssh/options", status=200)
    assert (
        await supervisor_client.addons.addon_options(
            "core_ssh",
            AddonsOptions(
                config=None,
                boot=AddonBoot.AUTO,
                network={"22/tcp": 22, "1234/tcp": None},
                watchdog=True,
            ),
        )
        is None
    )
    assert len(responses.requests) == 1
    assert (
        request := responses.requests[
            ("POST", URL(f"{SUPERVISOR_URL}/addons/core_ssh/options"))
        ]
    )
    assert request[0].kwargs["json"] == {
        "options": None,
        "boot": "auto",
        "network": {"22/tcp": 22, "1234/tcp": None},
        "watchdog": True,
    }


async def test_addons_config_validate(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test config validate API."""
    responses.post(
        f"{SUPERVISOR_URL}/addons/core_ssh/options/validate",
        status=200,
        body=load_fixture("addons_config_validate.json"),
    )
    validate = await supervisor_client.addons.addon_config_validate(
        "core_ssh", {"bad": "config"}
    )
    assert validate.message == (
        "Missing option 'server' in root in Terminal & SSH"
        " (core_ssh). Got {'bad': 'config'}"
    )
    assert validate.valid is False
    assert validate.pwned is False


async def test_addons_config(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test get addon config API."""
    responses.get(
        f"{SUPERVISOR_URL}/addons/core_ssh/options/config",
        status=200,
        body=load_fixture("addons_options_config.json"),
    )
    config = await supervisor_client.addons.addon_config("core_ssh")
    assert config["authorized_keys"] == []
    assert config["password"] == ""


async def test_addons_rebuild(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test rebuild addon API."""
    responses.post(f"{SUPERVISOR_URL}/addons/local_example/rebuild", status=200)
    assert await supervisor_client.addons.rebuild_addon("local_example") is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/addons/local_example/rebuild"))
    }


async def test_addons_stdin(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test addon stdin API."""
    responses.post(f"{SUPERVISOR_URL}/addons/core_ssh/stdin", status=200)
    assert (
        await supervisor_client.addons.addon_stdin("core_ssh", b"hello world") is None
    )
    assert len(responses.requests) == 1
    assert (
        request := responses.requests[
            ("POST", URL(f"{SUPERVISOR_URL}/addons/core_ssh/stdin"))
        ]
    )
    assert request[0].kwargs["data"] == b"hello world"


async def test_addons_security(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test addon security API."""
    responses.post(f"{SUPERVISOR_URL}/addons/core_ssh/security", status=200)
    assert (
        await supervisor_client.addons.addon_security(
            "core_ssh", AddonsSecurityOptions(protected=True)
        )
        is None
    )
    assert len(responses.requests) == 1
    assert (
        request := responses.requests[
            ("POST", URL(f"{SUPERVISOR_URL}/addons/core_ssh/security"))
        ]
    )
    assert request[0].kwargs["json"] == {"protected": True}


async def test_addons_stats(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test addon stats API."""
    responses.get(
        f"{SUPERVISOR_URL}/addons/core_ssh/stats",
        status=200,
        body=load_fixture("addon_stats.json"),
    )
    stats = await supervisor_client.addons.addon_stats("core_ssh")
    assert stats.cpu_percent == 0
    assert stats.memory_usage == 24588288
    assert stats.network_rx == 1717120021


async def test_addons_serialize_by_alias() -> None:
    """Test serializing addons by alias."""
    response = Response.from_json(load_fixture("store_addon_info.json"))
    store_addon_info = StoreAddonComplete.from_dict(response.data)

    assert store_addon_info.supervisor_api is False
    assert (store_addon_info.to_dict())["supervisor_api"] is False
    assert (store_addon_info.to_dict(by_alias=True))["hassio_api"] is False

    response = Response.from_json(load_fixture("addons_info.json"))
    addon_info = InstalledAddonComplete.from_dict(response.data)

    assert addon_info.supervisor_api is True
    assert (addon_info.to_dict())["supervisor_api"] is True
    assert (addon_info.to_dict(by_alias=True))["hassio_api"] is True
