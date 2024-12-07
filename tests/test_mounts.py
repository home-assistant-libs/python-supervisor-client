"""Test mounts supervisor client."""

from pathlib import PurePath

from aioresponses import aioresponses
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import (
    CIFSMountRequest,
    MountCifsVersion,
    MountsOptions,
    MountUsage,
    NFSMountRequest,
)

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_mounts_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test mounts info API."""
    responses.get(
        f"{SUPERVISOR_URL}/mounts", status=200, body=load_fixture("mounts_info.json")
    )
    info = await supervisor_client.mounts.info()
    assert info.default_backup_mount == "Test"

    assert info.mounts[0].name == "Test"
    assert info.mounts[0].server == "test.local"
    assert info.mounts[0].type == "cifs"
    assert info.mounts[0].share == "backup"
    assert info.mounts[0].usage == "backup"
    assert info.mounts[0].read_only is False
    assert info.mounts[0].version is None
    assert info.mounts[0].state == "active"
    assert info.mounts[0].user_path is None

    assert info.mounts[1].usage == "share"
    assert info.mounts[1].read_only is True
    assert info.mounts[1].version == "2.0"
    assert info.mounts[1].port == 12345
    assert info.mounts[1].user_path == PurePath("/share/Test2")

    assert info.mounts[2].type == "nfs"
    assert info.mounts[2].usage == "media"
    assert info.mounts[2].path.as_posix() == "media"
    assert info.mounts[2].user_path == PurePath("/media/Test3")


@pytest.mark.parametrize("mount_name", ["test", None])
async def test_mounts_options(
    responses: aioresponses, supervisor_client: SupervisorClient, mount_name: str | None
) -> None:
    """Test mounts options API."""
    responses.post(f"{SUPERVISOR_URL}/mounts/options", status=200)
    assert (
        await supervisor_client.mounts.options(
            MountsOptions(default_backup_mount=mount_name)
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/mounts/options"))
    }


@pytest.mark.parametrize(
    "mount_config",
    [
        CIFSMountRequest(
            server="test.local",
            share="backup",
            usage=MountUsage.BACKUP,
        ),
        CIFSMountRequest(
            server="test.local",
            share="media",
            port=12345,
            usage=MountUsage.MEDIA,
            version=MountCifsVersion.LEGACY_2_0,
            read_only=True,
            username="test",
            password="test",  # noqa: S106
        ),
        NFSMountRequest(
            server="test.local",
            path=PurePath("share"),
            usage=MountUsage.SHARE,
        ),
        NFSMountRequest(
            server="test.local",
            path=PurePath("backups"),
            port=12345,
            read_only=False,
            usage=MountUsage.BACKUP,
        ),
    ],
)
async def test_create_mount(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    mount_config: CIFSMountRequest | NFSMountRequest,
) -> None:
    """Test create mount API."""
    responses.post(f"{SUPERVISOR_URL}/mounts", status=200)
    assert await supervisor_client.mounts.create_mount("test", mount_config) is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/mounts"))}


@pytest.mark.parametrize(
    "mount_config",
    [
        CIFSMountRequest(
            server="test.local",
            share="backup",
            usage=MountUsage.BACKUP,
        ),
        CIFSMountRequest(
            server="test.local",
            share="media",
            port=12345,
            usage=MountUsage.MEDIA,
            version=MountCifsVersion.LEGACY_2_0,
            read_only=True,
            username="test",
            password="test",  # noqa: S106
        ),
        NFSMountRequest(
            server="test.local",
            path=PurePath("share"),
            usage=MountUsage.SHARE,
        ),
        NFSMountRequest(
            server="test.local",
            path=PurePath("backups"),
            port=12345,
            read_only=False,
            usage=MountUsage.BACKUP,
        ),
    ],
)
async def test_update_mount(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    mount_config: CIFSMountRequest | NFSMountRequest,
) -> None:
    """Test update mount API."""
    responses.put(f"{SUPERVISOR_URL}/mounts/test", status=200)
    assert await supervisor_client.mounts.update_mount("test", mount_config) is None
    assert responses.requests.keys() == {("PUT", URL(f"{SUPERVISOR_URL}/mounts/test"))}


async def test_delete_mount(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test delete mount API."""
    responses.delete(f"{SUPERVISOR_URL}/mounts/test", status=200)
    assert await supervisor_client.mounts.delete_mount("test") is None
    assert responses.requests.keys() == {
        ("DELETE", URL(f"{SUPERVISOR_URL}/mounts/test"))
    }


async def test_reload_mount(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test reload mount API."""
    responses.post(f"{SUPERVISOR_URL}/mounts/test/reload", status=200)
    assert await supervisor_client.mounts.reload_mount("test") is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/mounts/test/reload"))
    }
