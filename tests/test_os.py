"""Test OS supervisor client."""

from pathlib import PurePath

from aiointercept import aiointercept
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import (
    BootSlotName,
    GreenOptions,
    MigrateDataOptions,
    OSUpdate,
    SetBootSlotOptions,
    YellowOptions,
)
from aiohasupervisor.models.os import SwapOptions

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_os_info(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS info API."""
    responses.get(
        f"{SUPERVISOR_URL}/os/info",
        status=200,
        body=load_fixture("os_info.json"),
    )
    info = await supervisor_client.os.info()
    assert info.version == "13.0"
    assert info.version_latest == "13.1"
    assert info.version_pending is None
    assert info.update_available is True
    assert info.boot_slots["A"].state == "inactive"
    assert info.boot_slots["B"].state == "booted"
    assert info.boot_slots["B"].status == "good"
    assert info.boot_slots["B"].version == "13.0"


@pytest.mark.parametrize("options", [None, OSUpdate(version="13.0")])
async def test_os_update(
    responses: aiointercept,
    supervisor_client: SupervisorClient,
    options: OSUpdate | None,
) -> None:
    """Test OS update API."""
    responses.post(f"{SUPERVISOR_URL}/os/update", status=200)
    assert await supervisor_client.os.update(options) is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/os/update"))}


async def test_os_swap_info(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS config swap API."""
    responses.get(
        f"{SUPERVISOR_URL}/os/config/swap",
        status=200,
        body=load_fixture("os_config_swap.json"),
    )
    info = await supervisor_client.os.swap_info()
    assert info.swap_size == "1G"
    assert info.swappiness == 1


async def test_os_set_swap_options(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS set swap options API."""
    responses.post(f"{SUPERVISOR_URL}/os/config/swap", status=200)
    assert (
        await supervisor_client.os.set_swap_options(
            SwapOptions(swap_size="1G", swappiness=20)
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/os/config/swap"))
    }


async def test_os_config_sync(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS config sync API."""
    responses.post(f"{SUPERVISOR_URL}/os/config/sync", status=200)
    assert await supervisor_client.os.config_sync() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/os/config/sync"))
    }


async def test_os_migrate_data(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS migrate data API."""
    responses.post(f"{SUPERVISOR_URL}/os/datadisk/move", status=200)
    assert (
        await supervisor_client.os.migrate_data(MigrateDataOptions(device="/dev/test"))
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/os/datadisk/move"))
    }


async def test_os_list_data_disks(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS datadisk list API."""
    responses.get(
        f"{SUPERVISOR_URL}/os/datadisk/list",
        status=200,
        body=load_fixture("os_datadisk_list.json"),
    )
    datadisks = await supervisor_client.os.list_data_disks()
    assert datadisks[0].vendor == "SSK"
    assert datadisks[0].model == "SSK Storage"
    assert datadisks[0].serial == "DF123"
    assert datadisks[0].name == "SSK SSK Storage (DF123)"
    assert datadisks[0].dev_path == PurePath("/dev/sda")


async def test_os_wipe_data(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS wipe data API."""
    responses.post(f"{SUPERVISOR_URL}/os/datadisk/wipe", status=200)
    assert await supervisor_client.os.wipe_data() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/os/datadisk/wipe"))
    }


async def test_os_set_boot_slot(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS set boot slot API."""
    responses.post(f"{SUPERVISOR_URL}/os/boot-slot", status=200)
    assert (
        await supervisor_client.os.set_boot_slot(
            SetBootSlotOptions(boot_slot=BootSlotName.B)
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/os/boot-slot"))
    }


async def test_os_green_info(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS green board info API."""
    responses.get(
        f"{SUPERVISOR_URL}/os/boards/green",
        status=200,
        body=load_fixture("os_green_info.json"),
    )
    info = await supervisor_client.os.green_info()
    assert info.activity_led is True
    assert info.power_led is True
    assert info.system_health_led is True


async def test_os_green_options(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS green board options API."""
    responses.post(f"{SUPERVISOR_URL}/os/boards/green", status=200)
    assert (
        await supervisor_client.os.set_green_options(GreenOptions(activity_led=False))
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/os/boards/green"))
    }


async def test_os_yellow_info(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS yellow board info API."""
    responses.get(
        f"{SUPERVISOR_URL}/os/boards/yellow",
        status=200,
        body=load_fixture("os_yellow_info.json"),
    )
    info = await supervisor_client.os.yellow_info()
    assert info.disk_led is True
    assert info.heartbeat_led is True
    assert info.power_led is True


async def test_os_yellow_options(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test OS yellow board options API."""
    responses.post(f"{SUPERVISOR_URL}/os/boards/yellow", status=200)
    assert (
        await supervisor_client.os.set_yellow_options(
            YellowOptions(heartbeat_led=False)
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/os/boards/yellow"))
    }


async def test_os_raspberry_pi_firmware_info(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test Raspberry Pi firmware info API."""
    responses.get(
        f"{SUPERVISOR_URL}/os/boards/raspberrypi/firmware",
        status=200,
        body=load_fixture("os_raspberrypi_info.json"),
    )
    info = await supervisor_client.os.raspberry_pi_firmware_info()
    assert info.current_version == "1765222194"
    assert info.latest_version == "1778498402"
    assert info.update_available is True
    assert info.update_blocked is False
    assert info.update_pending is False
    assert info.blocked_reason is None


async def test_os_update_raspberry_pi_firmware(
    responses: aiointercept, supervisor_client: SupervisorClient
) -> None:
    """Test Raspberry Pi firmware update API."""
    responses.post(
        f"{SUPERVISOR_URL}/os/boards/raspberrypi/firmware/update", status=200
    )
    assert await supervisor_client.os.update_raspberry_pi_firmware() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/os/boards/raspberrypi/firmware/update"))
    }
