from pydantic import BaseModel, Field


class Msg(BaseModel):
    message: str = Field(..., description="Human-readable message")
