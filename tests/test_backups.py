"""Test backups supervisor client."""

from datetime import UTC, datetime
from typing import Any

from aioresponses import CallbackResult, aioresponses
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import (
    BackupsOptions,
    Folder,
    FreezeOptions,
    FullBackupOptions,
    PartialBackupOptions,
    PartialRestoreOptions,
)

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_backups_list(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test backups list API."""
    responses.get(
        f"{SUPERVISOR_URL}/backups", status=200, body=load_fixture("backups_list.json")
    )
    backups = await supervisor_client.backups.list()
    assert backups[0].slug == "58bc7491"
    assert backups[0].type == "full"
    assert backups[0].date == datetime(2024, 4, 6, 7, 5, 40, 0, UTC)
    assert backups[0].compressed is True
    assert backups[0].content.homeassistant is True
    assert backups[0].content.folders == ["share", "addons/local", "ssl", "media"]
    assert backups[1].slug == "69558789"
    assert backups[1].type == "partial"


async def test_backups_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test backups info API."""
    responses.get(
        f"{SUPERVISOR_URL}/backups/info",
        status=200,
        body=load_fixture("backups_info.json"),
    )
    info = await supervisor_client.backups.info()
    assert info.backups[0].slug == "58bc7491"
    assert info.backups[1].slug == "69558789"
    assert info.days_until_stale == 30


async def test_backups_options(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test backups options API."""
    responses.post(f"{SUPERVISOR_URL}/backups/options", status=200)
    assert (
        await supervisor_client.backups.options(BackupsOptions(days_until_stale=10))
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/backups/options"))
    }


async def test_backups_reload(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test backups reload API."""
    responses.post(f"{SUPERVISOR_URL}/backups/reload", status=200)
    assert await supervisor_client.backups.reload() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/backups/reload"))
    }


@pytest.mark.parametrize("options", [None, FreezeOptions(timeout=1000)])
async def test_backups_freeze(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: FreezeOptions | None,
) -> None:
    """Test backups freeze API."""
    responses.post(f"{SUPERVISOR_URL}/backups/freeze", status=200)
    assert await supervisor_client.backups.freeze(options) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/backups/freeze"))
    }


async def test_backups_thaw(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test backups thaw API."""
    responses.post(f"{SUPERVISOR_URL}/backups/thaw", status=200)
    assert await supervisor_client.backups.thaw() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/backups/thaw"))
    }


async def test_partial_backup_options() -> None:
    """Test partial backup options."""
    assert PartialBackupOptions(name="good", addons={"a"})
    assert PartialBackupOptions(name="good", folders={Folder.SSL})
    assert PartialBackupOptions(name="good", homeassistant=True)
    with pytest.raises(
        ValueError,
        match="At least one of addons, folders, or homeassistant must have a value",
    ):
        PartialBackupOptions(name="bad")


async def test_partial_restore_options() -> None:
    """Test partial restore options."""
    assert PartialRestoreOptions(addons={"a"})
    assert PartialRestoreOptions(folders={Folder.SSL})
    assert PartialRestoreOptions(homeassistant=True)
    with pytest.raises(
        ValueError,
        match="At least one of addons, folders, or homeassistant must have a value",
    ):
        PartialRestoreOptions(background=True)


def backup_callback(url: str, **kwargs: dict[str, Any]) -> CallbackResult:  # noqa: ARG001
    """Return response based on whether backup was in background or not."""
    if kwargs["json"] and kwargs["json"]["background"]:
        fixture = "backup_background.json"
    else:
        fixture = "backup_foreground.json"
    return CallbackResult(status=200, body=load_fixture(fixture))


@pytest.mark.parametrize(
    ("options", "slug"),
    [
        (FullBackupOptions(name="Test", background=True), None),
        (FullBackupOptions(name="Test", background=False), "9ecf0028"),
        (None, "9ecf0028"),
    ],
)
async def test_backups_full_backup(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: FullBackupOptions | None,
    slug: str | None,
) -> None:
    """Test backups full backup API."""
    responses.post(
        f"{SUPERVISOR_URL}/backups/new/full",
        callback=backup_callback,
    )
    result = await supervisor_client.backups.full_backup(options)
    assert result.job_id == "dc9dbc16f6ad4de592ffa72c807ca2bf"
    assert result.slug == slug


@pytest.mark.parametrize(
    ("background", "slug"),
    [(True, None), (False, "9ecf0028")],
)
async def test_backups_partial_backup(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    background: bool,  # noqa: FBT001
    slug: str | None,
) -> None:
    """Test backups full backup API."""
    responses.post(
        f"{SUPERVISOR_URL}/backups/new/partial",
        callback=backup_callback,
    )
    result = await supervisor_client.backups.partial_backup(
        PartialBackupOptions(name="test", background=background, addons={"core_ssh"})
    )
    assert result.job_id == "dc9dbc16f6ad4de592ffa72c807ca2bf"
    assert result.slug == slug


async def test_backup_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test backup info API."""
    responses.get(
        f"{SUPERVISOR_URL}/backups/69558789/info",
        status=200,
        body=load_fixture("backup_info.json"),
    )
    result = await supervisor_client.backups.backup_info("69558789")
    assert result.slug == "69558789"
    assert result.type == "partial"
    assert result.date == datetime(2024, 5, 31, 0, 0, 0, 0, UTC)
    assert result.size == 0.01
    assert result.compressed is True
    assert result.addons[0].slug == "core_mosquitto"
    assert result.addons[0].name == "Mosquitto broker"
    assert result.addons[0].version == "6.4.0"
    assert result.addons[0].size == 0
    assert result.repositories == [
        "core",
        "local",
        "https://github.com/music-assistant/home-assistant-addon",
        "https://github.com/esphome/home-assistant-addon",
        "https://github.com/hassio-addons/repository",
    ]
    assert result.folders == []
    assert result.homeassistant_exclude_database is None


async def test_remove_backup(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test remove backup API."""
    responses.delete(f"{SUPERVISOR_URL}/backups/abc123", status=200)
    assert await supervisor_client.backups.remove_backup("abc123") is None
    assert responses.requests.keys() == {
        ("DELETE", URL(f"{SUPERVISOR_URL}/backups/abc123"))
    }


async def test_full_restore(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test full restore API."""
    responses.post(
        f"{SUPERVISOR_URL}/backups/abc123/restore/full",
        status=200,
        body=load_fixture("backup_restore.json"),
    )
    result = await supervisor_client.backups.full_restore("abc123")
    assert result.job_id == "dc9dbc16f6ad4de592ffa72c807ca2bf"


async def test_partial_restore(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test partial restore API."""
    responses.post(
        f"{SUPERVISOR_URL}/backups/abc123/restore/partial",
        status=200,
        body=load_fixture("backup_restore.json"),
    )
    result = await supervisor_client.backups.partial_restore(
        "abc123", PartialRestoreOptions(addons={"core_ssh"})
    )
    assert result.job_id == "dc9dbc16f6ad4de592ffa72c807ca2bf"
