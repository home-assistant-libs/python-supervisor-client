"""Test mounts supervisor client."""

from pathlib import PurePath

from aiointercept import aiointercept
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import (
    CIFSMountRequest,
    DiskMountRequest,
    MountCifsVersion,
    MountsOptions,
    MountUsage,
    NFSMountRequest,
)

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_mounts_info(
    responses: aiointercept, supervisor_client: SupervisorClient
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

    assert info.mounts[3].type == "disk"
    assert info.mounts[3].usage == "media"
    assert info.mounts[3].read_only is True
    assert info.mounts[3].uuid == "C45A-110F"
    assert info.mounts[3].filesystem == "vfat"
    assert info.mounts[3].user_path == PurePath("/media/Test4")

    assert info.mounts[4].type == "disk"
    assert info.mounts[4].usage is MountUsage.BACKUP
    assert info.mounts[4].filesystem is None
    assert info.mounts[4].state is None


async def test_mounts_info_skips_unknown_type(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test a mount type this client does not know is skipped, not an error."""
    responses.get(
        f"{SUPERVISOR_URL}/mounts",
        status=200,
        body=load_fixture("mounts_info_unknown_type.json"),
    )
    info = await supervisor_client.mounts.info()
    assert [mount.name for mount in info.mounts] == ["Test"]


@pytest.mark.parametrize("mount_name", ["test", None])
async def test_mounts_options(
    responses: aiointercept, supervisor_client: SupervisorClient, mount_name: str | None
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
        DiskMountRequest(usage=MountUsage.MEDIA, uuid="C45A-110F"),
        DiskMountRequest(
            usage=MountUsage.SHARE,
            device="/dev/sda1",
            uuid="C45A-110F",
            read_only=True,
        ),
    ],
)
async def test_create_mount(
    responses: aiointercept,
    supervisor_client: SupervisorClient,
    mount_config: CIFSMountRequest | NFSMountRequest | DiskMountRequest,
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
        DiskMountRequest(usage=MountUsage.MEDIA, uuid="C45A-110F"),
        DiskMountRequest(
            usage=MountUsage.SHARE,
            device="/dev/sda1",
            uuid="C45A-110F",
            read_only=True,
        ),
    ],
)
async def test_update_mount(
    responses: aiointercept,
    supervisor_client: SupervisorClient,
    mount_config: CIFSMountRequest | NFSMountRequest | DiskMountRequest,
) -> None:
    """Test update mount API."""
    responses.put(f"{SUPERVISOR_URL}/mounts/test", status=200)
    assert await supervisor_client.mounts.update_mount("test", mount_config) is None
    assert responses.requests.keys() == {("PUT", URL(f"{SUPERVISOR_URL}/mounts/test"))}


@pytest.mark.parametrize(
    ("mount_config", "expected_body"),
    [
        (
            CIFSMountRequest(
                server="test.local", share="media", usage=MountUsage.MEDIA
            ),
            {
                "type": "cifs",
                "server": "test.local",
                "share": "media",
                "usage": "media",
            },
        ),
        (
            NFSMountRequest(
                server="test.local", path=PurePath("share"), usage=MountUsage.SHARE
            ),
            {"type": "nfs", "server": "test.local", "path": "share", "usage": "share"},
        ),
        (
            DiskMountRequest(usage=MountUsage.MEDIA, uuid="C45A-110F", read_only=True),
            {"type": "disk", "usage": "media", "uuid": "C45A-110F", "read_only": True},
        ),
        (
            DiskMountRequest(usage=MountUsage.MEDIA, device="/dev/sda1"),
            {"type": "disk", "usage": "media", "device": "/dev/sda1"},
        ),
    ],
)
async def test_mount_request_body(
    responses: aiointercept,
    supervisor_client: SupervisorClient,
    mount_config: CIFSMountRequest | NFSMountRequest | DiskMountRequest,
    expected_body: dict[str, str | bool],
) -> None:
    """Test create and update send the type although it is the default."""
    responses.post(f"{SUPERVISOR_URL}/mounts", status=200)
    responses.put(f"{SUPERVISOR_URL}/mounts/test", status=200)
    await supervisor_client.mounts.create_mount("test", mount_config)
    await supervisor_client.mounts.update_mount("test", mount_config)
    post = responses.requests[("POST", URL(f"{SUPERVISOR_URL}/mounts"))]
    put = responses.requests[("PUT", URL(f"{SUPERVISOR_URL}/mounts/test"))]
    assert post[0].kwargs["json"] == {"name": "test", **expected_body}
    assert put[0].kwargs["json"] == expected_body


def test_disk_mount_request_needs_identifier() -> None:
    """Test a disk mount request without device or uuid is refused."""
    with pytest.raises(ValueError, match="device or uuid"):
        DiskMountRequest(usage=MountUsage.MEDIA)


async def test_delete_mount(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test delete mount API."""
    responses.delete(f"{SUPERVISOR_URL}/mounts/test", status=200)
    assert await supervisor_client.mounts.delete_mount("test") is None
    assert responses.requests.keys() == {
        ("DELETE", URL(f"{SUPERVISOR_URL}/mounts/test"))
    }


async def test_reload_mount(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test reload mount API."""
    responses.post(f"{SUPERVISOR_URL}/mounts/test/reload", status=200)
    assert await supervisor_client.mounts.reload_mount("test") is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/mounts/test/reload"))
    }
