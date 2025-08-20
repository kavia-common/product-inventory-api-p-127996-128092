from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    product_id: int = Field(..., description="Product ID")
    location_id: int = Field(..., description="Location ID")
    quantity: int = Field(..., ge=0)


class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0)


class InventoryOut(BaseModel):
    id: int
    product_id: int
    location_id: int
    quantity: int

    class Config:
        from_attributes = True
