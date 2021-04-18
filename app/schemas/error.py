from pydantic import BaseModel


class Error(BaseModel):
    status: int
    type: str
    message: str
