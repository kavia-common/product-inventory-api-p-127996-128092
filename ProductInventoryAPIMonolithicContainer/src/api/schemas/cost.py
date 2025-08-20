from pydantic import BaseModel, Field


class CostCreate(BaseModel):
    product_id: int
    unit_cost: float = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=8)


class CostOut(BaseModel):
    id: int
    product_id: int
    unit_cost: float
    currency: str

    class Config:
        from_attributes = True
