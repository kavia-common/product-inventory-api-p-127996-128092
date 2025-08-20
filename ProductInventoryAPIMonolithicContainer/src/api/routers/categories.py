from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import require_roles
from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter()


# PUBLIC_INTERFACE
@router.post("", summary="Create category", response_model=CategoryOut, dependencies=[Depends(require_roles("admin", "manager"))])
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    """This is a public function."""
    if db.query(Category).filter(Category.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Category exists")
    cat = Category(**payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# PUBLIC_INTERFACE
@router.get("", summary="List categories", response_model=List[CategoryOut], dependencies=[Depends(require_roles("admin", "manager", "viewer"))])
def list_categories(db: Session = Depends(get_db)):
    """This is a public function."""
    return db.query(Category).order_by(Category.id.desc()).all()


# PUBLIC_INTERFACE
@router.patch("/{category_id}", summary="Update category", response_model=CategoryOut, dependencies=[Depends(require_roles("admin", "manager"))])
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    """This is a public function."""
    c = db.get(Category, category_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# PUBLIC_INTERFACE
@router.delete("/{category_id}", summary="Delete category", dependencies=[Depends(require_roles("admin"))])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """This is a public function."""
    c = db.get(Category, category_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(c)
    db.commit()
    return {"message": "deleted"}
