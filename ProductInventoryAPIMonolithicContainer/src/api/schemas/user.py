from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., description="Unique username")
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: str = Field(default="manager", description="admin, manager, viewer")


class UserOut(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True
