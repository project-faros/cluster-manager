from pydantic import BaseModel


class BastionConfig(BaseModel):
    become_pass: str
