from typing import Optional

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    code: str = Field(..., max_length=64)
    name: str = Field(..., max_length=128)
    address: Optional[str] = Field(default=None, max_length=512)


class LocationUpdate(BaseModel):
    code: Optional[str] = Field(default=None, max_length=64)
    name: Optional[str] = Field(default=None, max_length=128)
    address: Optional[str] = Field(default=None, max_length=512)


class LocationOut(BaseModel):
    id: int
    code: str
    name: str
    address: Optional[str] = None

    class Config:
        from_attributes = True
