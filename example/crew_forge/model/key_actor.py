from pydantic import BaseModel


class KeyActor(BaseModel):
    name: str
    description: str