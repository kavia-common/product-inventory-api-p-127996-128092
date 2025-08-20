from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: str = Field(..., max_length=64)
    name: str = Field(..., max_length=256)
    description: Optional[str] = Field(default=None)
    category_id: Optional[int] = Field(default=None)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None)
    category_id: Optional[int] = Field(default=None)


class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None

    class Config:
        from_attributes = True
