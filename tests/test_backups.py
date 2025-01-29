"""Test backups supervisor client."""

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import PurePath
from typing import Any

from aioresponses import CallbackResult, aioresponses
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import (
    AddonSet,
    BackupLocationAttributes,
    BackupsOptions,
    DownloadBackupOptions,
    Folder,
    FreezeOptions,
    FullBackupOptions,
    FullRestoreOptions,
    PartialBackupOptions,
    PartialRestoreOptions,
    RemoveBackupOptions,
    UploadBackupOptions,
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
        await supervisor_client.backups.set_options(BackupsOptions(days_until_stale=10))
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


async def test_backup_options_location() -> None:
    """Test location field in backup options."""
    assert FullBackupOptions(location=["test", None]).to_dict() == {
        "location": ["test", None]
    }
    assert FullBackupOptions(location="test").to_dict() == {"location": "test"}
    assert FullBackupOptions().to_dict() == {}

    assert PartialBackupOptions(
        location=["test", ".local"], folders={Folder.SSL}
    ).to_dict() == {
        "location": ["test", ".local"],
        "folders": ["ssl"],
    }
    assert PartialBackupOptions(location="test", folders={Folder.SSL}).to_dict() == {
        "location": "test",
        "folders": ["ssl"],
    }
    assert PartialBackupOptions(folders={Folder.SSL}).to_dict() == {"folders": ["ssl"]}


def backup_callback(url: str, **kwargs: dict[str, Any]) -> CallbackResult:  # noqa: ARG001
    """Return response based on whether backup was in background or not."""
    if kwargs["json"] and kwargs["json"].get("background"):
        fixture = "backup_background.json"
    else:
        fixture = "backup_foreground.json"
    return CallbackResult(status=200, body=load_fixture(fixture))


@pytest.mark.parametrize(
    ("options", "slug"),
    [
        (FullBackupOptions(name="Test", background=True), None),
        (FullBackupOptions(name="Test", background=False), "9ecf0028"),
        (FullBackupOptions(name="Test", background=False, location="test"), "9ecf0028"),
        (
            FullBackupOptions(
                name="Test", background=False, location={".local", "test"}
            ),
            "9ecf0028",
        ),
        (
            FullBackupOptions(
                name="Test", background=False, extra={"user": "test", "scheduled": True}
            ),
            "9ecf0028",
        ),
        (FullBackupOptions(name="Test", background=False, extra=None), "9ecf0028"),
        (
            FullBackupOptions(
                name="test", background=False, filename=PurePath("backup.tar")
            ),
            "9ecf0028",
        ),
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
    assert result.job_id.hex == "dc9dbc16f6ad4de592ffa72c807ca2bf"
    assert result.slug == slug


@pytest.mark.parametrize(
    ("options", "slug"),
    [
        (PartialBackupOptions(name="Test", background=True, addons={"core_ssh"}), None),
        (
            PartialBackupOptions(name="Test", background=False, addons={"core_ssh"}),
            "9ecf0028",
        ),
        (
            PartialBackupOptions(
                name="Test", background=False, location="test", addons={"core_ssh"}
            ),
            "9ecf0028",
        ),
        (
            PartialBackupOptions(
                name="Test",
                background=False,
                location={".local", "test"},
                addons={"core_ssh"},
            ),
            "9ecf0028",
        ),
        (
            PartialBackupOptions(
                name="Test",
                background=False,
                addons={"core_ssh"},
                extra={"user": "test", "scheduled": True},
            ),
            "9ecf0028",
        ),
        (
            PartialBackupOptions(
                name="Test", background=False, addons={"core_ssh"}, extra=None
            ),
            "9ecf0028",
        ),
        (
            PartialBackupOptions(
                name="Test",
                background=False,
                addons={"core_ssh"},
                filename=PurePath("backup.tar"),
            ),
            "9ecf0028",
        ),
        (
            PartialBackupOptions(name="Test", background=None, addons={"core_ssh"}),
            "9ecf0028",
        ),
        (
            PartialBackupOptions(name="Test", background=None, addons=AddonSet.ALL),
            "9ecf0028",
        ),
    ],
)
async def test_backups_partial_backup(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: PartialBackupOptions,
    slug: str | None,
) -> None:
    """Test backups full backup API."""
    responses.post(
        f"{SUPERVISOR_URL}/backups/new/partial",
        callback=backup_callback,
    )
    result = await supervisor_client.backups.partial_backup(options)
    assert result.job_id.hex == "dc9dbc16f6ad4de592ffa72c807ca2bf"
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
    assert result.extra is None
    assert result.location_attributes[".local"].protected is False
    assert result.location_attributes[".local"].size_bytes == 10123


async def test_backup_info_no_homeassistant(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test backup info API with no home assistant."""
    responses.get(
        f"{SUPERVISOR_URL}/backups/d13dedd0/info",
        status=200,
        body=load_fixture("backup_info_no_homeassistant.json"),
    )
    result = await supervisor_client.backups.backup_info("d13dedd0")
    assert result.slug == "d13dedd0"
    assert result.type == "partial"
    assert result.homeassistant is None


async def test_backup_info_with_extra(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test backup info API with extras set by client."""
    responses.get(
        f"{SUPERVISOR_URL}/backups/d13dedd0/info",
        status=200,
        body=load_fixture("backup_info_with_extra.json"),
    )
    result = await supervisor_client.backups.backup_info("d13dedd0")
    assert result.slug == "69558789"
    assert result.type == "partial"
    assert result.extra == {"user": "test", "scheduled": True}


async def test_backup_info_with_multiple_locations(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test backup info API with multiple locations."""
    responses.get(
        f"{SUPERVISOR_URL}/backups/d13dedd0/info",
        status=200,
        body=load_fixture("backup_info_with_locations.json"),
    )
    result = await supervisor_client.backups.backup_info("d13dedd0")
    assert result.slug == "69558789"
    assert result.type == "partial"
    assert result.location_attributes[".local"].protected is False
    assert result.location_attributes[".local"].size_bytes == 10123
    assert result.location_attributes["Test"].protected is False
    assert result.location_attributes["Test"].size_bytes == 10123


@pytest.mark.parametrize(
    "options", [None, RemoveBackupOptions(location={"test", None})]
)
async def test_remove_backup(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: RemoveBackupOptions | None,
) -> None:
    """Test remove backup API."""
    responses.delete(f"{SUPERVISOR_URL}/backups/abc123", status=200)
    assert await supervisor_client.backups.remove_backup("abc123", options) is None
    assert responses.requests.keys() == {
        ("DELETE", URL(f"{SUPERVISOR_URL}/backups/abc123"))
    }


@pytest.mark.parametrize(
    "options",
    [
        None,
        FullRestoreOptions(password="abc123"),  # noqa: S106
        FullRestoreOptions(background=True),
        FullRestoreOptions(location="test"),
    ],
)
async def test_full_restore(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: FullRestoreOptions | None,
) -> None:
    """Test full restore API."""
    responses.post(
        f"{SUPERVISOR_URL}/backups/abc123/restore/full",
        status=200,
        body=load_fixture("backup_restore.json"),
    )
    result = await supervisor_client.backups.full_restore("abc123", options)
    assert result.job_id.hex == "dc9dbc16f6ad4de592ffa72c807ca2bf"


@pytest.mark.parametrize(
    "options",
    [
        PartialRestoreOptions(addons={"core_ssh"}),
        PartialRestoreOptions(homeassistant=True, location=".local"),
        PartialRestoreOptions(folders={Folder.SHARE, Folder.SSL}, location="test"),
        PartialRestoreOptions(addons={"core_ssh"}, background=True),
        PartialRestoreOptions(addons={"core_ssh"}, password="abc123"),  # noqa: S106
    ],
)
async def test_partial_restore(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: PartialRestoreOptions,
) -> None:
    """Test partial restore API."""
    responses.post(
        f"{SUPERVISOR_URL}/backups/abc123/restore/partial",
        status=200,
        body=load_fixture("backup_restore.json"),
    )
    result = await supervisor_client.backups.partial_restore("abc123", options)
    assert result.job_id.hex == "dc9dbc16f6ad4de592ffa72c807ca2bf"


@pytest.mark.parametrize(
    ("options", "query"),
    [
        (None, ""),
        (
            UploadBackupOptions(location={".local", "test"}),
            "?location=.local&location=test",
        ),
        (UploadBackupOptions(filename=PurePath("backup.tar")), "?filename=backup.tar"),
    ],
)
async def test_upload_backup(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: UploadBackupOptions | None,
    query: str,
) -> None:
    """Test upload backup API."""
    responses.post(
        f"{SUPERVISOR_URL}/backups/new/upload{query}",
        status=200,
        body=load_fixture("backup_uploaded.json"),
    )
    data = asyncio.StreamReader(loop=asyncio.get_running_loop())
    data.feed_data(b"backup test")
    data.feed_eof()

    result = await supervisor_client.backups.upload_backup(data, options)
    assert result == "7fed74c8"


@pytest.mark.parametrize(
    ("options", "query"),
    [
        (None, ""),
        (DownloadBackupOptions(location="test"), "?location=test"),
        (DownloadBackupOptions(location=None), "?location="),
    ],
)
async def test_download_backup(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    options: DownloadBackupOptions | None,
    query: str,
) -> None:
    """Test download backup API."""
    responses.get(
        f"{SUPERVISOR_URL}/backups/7fed74c8/download{query}",
        status=200,
        body=b"backup test",
    )
    result = await supervisor_client.backups.download_backup("7fed74c8", options)
    assert isinstance(result, AsyncIterator)
    async for chunk in result:
        assert chunk == b"backup test"


@pytest.mark.parametrize(
    ("options", "as_dict"),
    [
        (
            PartialBackupOptions(name="Test", folders={Folder.SHARE}),
            {"name": "Test", "folders": ["share"]},
        ),
        (PartialBackupOptions(addons={"core_ssh"}), {"addons": ["core_ssh"]}),
        (PartialBackupOptions(addons=AddonSet.ALL), {"addons": "ALL"}),
        (
            PartialBackupOptions(
                homeassistant=True, homeassistant_exclude_database=True
            ),
            {"homeassistant": True, "homeassistant_exclude_database": True},
        ),
        (
            PartialBackupOptions(
                folders={Folder.SSL}, compressed=True, background=True
            ),
            {"folders": ["ssl"], "compressed": True, "background": True},
        ),
        (
            PartialBackupOptions(
                homeassistant=True, location=[".cloud_backup", "test"]
            ),
            {"homeassistant": True, "location": [".cloud_backup", "test"]},
        ),
        (
            PartialBackupOptions(homeassistant=True, location="test"),
            {"homeassistant": True, "location": "test"},
        ),
        (
            PartialBackupOptions(homeassistant=True, filename=PurePath("backup.tar")),
            {"homeassistant": True, "filename": "backup.tar"},
        ),
    ],
)
async def test_partial_backup_model(
    options: PartialBackupOptions, as_dict: dict[str, Any]
) -> None:
    """Test partial backup model parsing and serializing."""
    assert PartialBackupOptions.from_dict(as_dict) == options
    assert options.to_dict() == as_dict


@pytest.mark.parametrize(
    ("options", "as_dict"),
    [
        (FullBackupOptions(name="Test"), {"name": "Test"}),
        (FullBackupOptions(password="test"), {"password": "test"}),  # noqa: S106
        (FullBackupOptions(compressed=True), {"compressed": True}),
        (
            FullBackupOptions(homeassistant_exclude_database=True),
            {"homeassistant_exclude_database": True},
        ),
        (FullBackupOptions(background=True), {"background": True}),
        (
            FullBackupOptions(location=[".cloud_backup", "test"]),
            {"location": [".cloud_backup", "test"]},
        ),
        (FullBackupOptions(location="test"), {"location": "test"}),
        (
            FullBackupOptions(filename=PurePath("backup.tar")),
            {"filename": "backup.tar"},
        ),
    ],
)
async def test_full_backup_model(
    options: FullBackupOptions, as_dict: dict[str, Any]
) -> None:
    """Test full backup model parsing and serializing."""
    assert FullBackupOptions.from_dict(as_dict) == options
    assert options.to_dict() == as_dict


async def test_backups_list_location_attributes(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
) -> None:
    """Test location attributes field in backups list."""
    responses.get(
        f"{SUPERVISOR_URL}/backups",
        status=200,
        body=load_fixture("backups_list_location_attributes.json"),
    )

    result = await supervisor_client.backups.list()
    assert result[0].location_attributes == {
        ".local": BackupLocationAttributes(
            protected=True,
            size_bytes=10240,
        ),
        "test": BackupLocationAttributes(
            protected=True,
            size_bytes=10240,
        ),
    }


async def test_backup_info_location_attributes(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
) -> None:
    """Test location attributes field in backup info."""
    responses.get(
        f"{SUPERVISOR_URL}/backups/d9c48f8b/info",
        status=200,
        body=load_fixture("backup_info_location_attributes.json"),
    )

    result = await supervisor_client.backups.backup_info("d9c48f8b")
    assert result.location_attributes == {
        ".local": BackupLocationAttributes(
            protected=True,
            size_bytes=10240,
        ),
        "test": BackupLocationAttributes(
            protected=True,
            size_bytes=10240,
        ),
    }
