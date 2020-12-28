from pydantic import BaseModel
from typing import List


class ProxyConfig(BaseModel):
    http: str
    https: str
    noproxy: List[str]
    ca: str
