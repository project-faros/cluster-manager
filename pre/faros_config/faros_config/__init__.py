from pydantic import BaseModel
from typing import Optional
import yaml

from .network import NetworkConfig
from .bastion import BastionConfig
from .cluster import ClusterConfig
from .proxy import ProxyConfig


class FarosConfig(BaseModel):
    network: NetworkConfig
    bastion: BastionConfig
    cluster: ClusterConfig
    proxy: Optional[ProxyConfig]

    @classmethod
    def from_yaml(cls, yaml_file: str) -> 'FarosConfig':
        with open(yaml_file) as f:
            config = yaml.safe_load(f)

        return cls.parse_obj(config)
