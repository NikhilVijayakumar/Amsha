from pydantic import BaseModel


class CorePrinciple(BaseModel):
    name: str
    description: str