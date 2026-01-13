from pydantic import BaseModel


class ProcessStep(BaseModel):
    step: int
    name: str
    description: str