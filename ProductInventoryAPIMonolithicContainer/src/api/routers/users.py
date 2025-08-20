from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import require_roles
from ..models.user import User
from ..schemas.user import UserCreate, UserOut
from ..core.security import get_password_hash

router = APIRouter()


# PUBLIC_INTERFACE
@router.post("", summary="Create user", response_model=UserOut, dependencies=[Depends(require_roles("admin"))])
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """This is a public function."""
    if db.query(User).filter((User.username == payload.username) | (User.email == payload.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already exists")
    user = User(
        username=payload.username,
        email=payload.email,
        role=payload.role,
        hashed_password=get_password_hash(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# PUBLIC_INTERFACE
@router.get("", summary="List users", response_model=List[UserOut], dependencies=[Depends(require_roles("admin"))])
def list_users(db: Session = Depends(get_db)):
    """This is a public function."""
    return db.query(User).all()


# PUBLIC_INTERFACE
@router.delete("/{user_id}", summary="Delete user", dependencies=[Depends(require_roles("admin"))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """This is a public function."""
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(u)
    db.commit()
    return {"message": "deleted"}
