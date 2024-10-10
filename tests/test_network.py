"""Test network supervisor client."""

from ipaddress import IPv4Address, IPv4Interface

from aioresponses import aioresponses
import pytest
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import (
    InterfaceMethod,
    IPv4Config,
    NetworkInterfaceConfig,
    VlanConfig,
)

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_network_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test network info API."""
    responses.get(
        f"{SUPERVISOR_URL}/network/info",
        status=200,
        body=load_fixture("network_info.json"),
    )
    result = await supervisor_client.network.info()
    assert result.interfaces[0].interface == "end0"
    assert result.interfaces[0].type == "ethernet"
    assert result.interfaces[0].enabled is True
    assert result.interfaces[0].mac == "00:11:22:33:44:55"
    assert result.interfaces[0].ipv4.method == "static"
    assert result.interfaces[0].ipv4.address[0].with_prefixlen == "192.168.1.2/24"
    assert result.interfaces[0].ipv4.nameservers[0].compressed == "192.168.1.1"
    assert result.interfaces[0].ipv4.gateway.compressed == "192.168.1.1"
    assert result.interfaces[0].ipv4.ready is True
    assert result.interfaces[0].ipv6.method == "disabled"
    assert (
        result.interfaces[0].ipv6.address[0].with_prefixlen
        == "fe80::819d:c479:d712:7a77/64"
    )
    assert result.interfaces[0].ipv6.gateway is None
    assert result.interfaces[0].wifi is None
    assert result.interfaces[0].vlan is None

    assert result.docker.interface == "hassio"
    assert result.docker.address.compressed == "172.30.32.0/23"
    assert result.docker.gateway.compressed == "172.30.32.1"
    assert result.docker.dns.compressed == "172.30.32.3"
    assert result.host_internet is True
    assert result.supervisor_internet is True


async def test_network_reload(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test network reload API."""
    responses.post(f"{SUPERVISOR_URL}/network/reload", status=200)
    assert await supervisor_client.network.reload() is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/network/reload"))
    }


async def test_network_interface_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test network interface info API."""
    responses.get(
        f"{SUPERVISOR_URL}/network/interface/end0/info",
        status=200,
        body=load_fixture("network_interface_info.json"),
    )
    result = await supervisor_client.network.interface_info("end0")
    assert result.interface == "end0"
    assert result.type == "ethernet"
    assert result.enabled is True
    assert result.mac == "00:11:22:33:44:55"
    assert result.ipv4.method == "static"
    assert result.ipv4.address[0].with_prefixlen == "192.168.1.2/24"
    assert result.ipv4.nameservers[0].compressed == "192.168.1.1"
    assert result.ipv4.gateway.compressed == "192.168.1.1"
    assert result.ipv4.ready is True
    assert result.ipv6.method == "disabled"
    assert result.ipv6.address[0].with_prefixlen == "fe80::819d:c479:d712:7a77/64"
    assert result.ipv6.gateway is None
    assert result.wifi is None
    assert result.vlan is None


async def test_network_update_interface(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test network interface update API."""
    responses.post(f"{SUPERVISOR_URL}/network/interface/end0/update", status=200)
    config = NetworkInterfaceConfig(
        ipv4=IPv4Config(
            method=InterfaceMethod.STATIC,
            address=[IPv4Interface("192.168.1.2/24")],
            gateway=IPv4Address("192.168.1.1"),
            nameservers=[IPv4Address("192.168.1.1")],
        )
    )
    assert (
        await supervisor_client.network.update_interface("end0", config=config) is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/network/interface/end0/update"))
    }


async def test_network_access_points(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test network access points API."""
    responses.get(
        f"{SUPERVISOR_URL}/network/interface/end0/accesspoints",
        status=200,
        body=load_fixture("network_access_points.json"),
    )
    result = await supervisor_client.network.access_points("end0")
    assert result[0].mode == "infrastructure"
    assert result[0].ssid == "UPC4814466"
    assert result[0].frequency == 2462
    assert result[0].signal == 47
    assert result[0].mac == "AA:BB:CC:DD:EE:FF"
    assert result[1].ssid == "VQ@35(55720"


@pytest.mark.parametrize(
    "config",
    [None, NetworkInterfaceConfig(ipv4=IPv4Config(method=InterfaceMethod.AUTO))],
)
async def test_network_save_vlan(
    responses: aioresponses,
    supervisor_client: SupervisorClient,
    config: NetworkInterfaceConfig | None,
) -> None:
    """Test network save vlan API."""
    responses.post(f"{SUPERVISOR_URL}/network/interface/end0/vlan/1", status=200)
    assert await supervisor_client.network.save_vlan("end0", 1, config=config) is None
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/network/interface/end0/vlan/1"))
    }


async def test_network_configs_cannot_be_empty() -> None:
    """Test network config instances require at least one field specified."""
    # Network interface config for update calls
    with pytest.raises(ValueError, match="At least one field must have a value"):
        NetworkInterfaceConfig()

    # Vlan config for save vlan calls
    with pytest.raises(ValueError, match="At least one field must have a value"):
        VlanConfig()
