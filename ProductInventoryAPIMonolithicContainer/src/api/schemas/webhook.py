from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class WebhookCreate(BaseModel):
    name: str = Field(..., max_length=128)
    url: HttpUrl
    secret: Optional[str] = Field(default=None, max_length=256)
    is_active: bool = True


class WebhookUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=128)
    url: Optional[HttpUrl] = None
    secret: Optional[str] = Field(default=None, max_length=256)
    is_active: Optional[bool] = None


class WebhookOut(BaseModel):
    id: int
    name: str
    url: str
    is_active: bool

    class Config:
        from_attributes = True
