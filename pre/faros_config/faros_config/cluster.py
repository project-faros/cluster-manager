from pydantic import BaseModel, constr
from typing import List, Optional

from .common import StrEnum

MacAddress = constr(regex=r'(([0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2})|(([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4})')  # noqa: E501


class ManagementProviderItem(StrEnum):
    ILO = "ilo"


class ManagementConfig(BaseModel):
    provider: ManagementProviderItem
    user: str
    password: str


class NodeConfig(BaseModel):
    name: str
    mac: MacAddress
    mgmt_mac: MacAddress
    install_drive: Optional[str]


class ClusterConfig(BaseModel):
    pull_secret: str
    management: ManagementConfig
    nodes: List[NodeConfig]
