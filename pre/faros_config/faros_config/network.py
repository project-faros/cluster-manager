from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network
from pydantic import BaseModel, constr
from typing import List, Union

from .common import StrEnum

MacAddress = constr(regex=r'(([0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2})|(([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4})')  # noqa: E501


class PortForwardConfigItem(StrEnum):
    SSH_TO_BASTION = "SSH to Bastion"
    HTTPS_TO_CLUSTER_API = "HTTPS to Cluster API"
    HTTP_TO_CLUSTER_APPS = "HTTP to Cluster Apps"
    HTTPS_TO_CLUSTER_APPS = "HTTPS to Cluster Apps"
    HTTPS_TO_COCKPIT_PANEL = "HTTPS to Cockpit Panel"


class NameMacPair(BaseModel):
    name: str
    mac: MacAddress


class NameMacIpSet(BaseModel):
    name: str
    mac: MacAddress
    ip: Union[IPv4Address, IPv6Address]


class DhcpConfig(BaseModel):
    ignore_macs: List[NameMacPair]
    extra_reservations: List[NameMacIpSet]


class LanConfig(BaseModel):
    subnet: Union[IPv4Network, IPv6Network]
    interfaces: List[str]
    dns_forward_resolvers: List[Union[IPv4Address, IPv6Address]]
    dhcp: DhcpConfig


class NetworkConfig(BaseModel):
    port_forward: List[PortForwardConfigItem]
    lan: LanConfig
