import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import create_access_token, verify_password, get_password_hash, get_current_user
from ..models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


class TokenOut(BaseModel):
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = "bearer"


# PUBLIC_INTERFACE
@router.post("/login", summary="Login and get JWT token", response_model=TokenOut)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """This is a public function."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning("Failed login for user '%s'", form_data.username)
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(subject=user.username)
    logger.info("User '%s' logged in", user.username)
    return TokenOut(access_token=token)


# PUBLIC_INTERFACE
@router.post("/seed-admin", summary="Create admin user if not exists", response_model=dict)
def seed_admin(username: str, password: str, email: str, db: Session = Depends(get_db)):
    """This is a public function."""
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return {"message": "Admin exists"}
    hashed = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed, role="admin", is_active=True)
    db.add(user)
    db.commit()
    logger.info("Seeded admin '%s'", username)
    return {"message": "Admin created"}


# PUBLIC_INTERFACE
@router.get("/me", summary="Get current user", response_model=dict)
def me(user: User = Depends(get_current_user)):
    """This is a public function."""
    return {"username": user.username, "email": user.email, "role": user.role, "is_active": user.is_active}
