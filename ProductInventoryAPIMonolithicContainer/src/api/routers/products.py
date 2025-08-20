from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import require_roles
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate, ProductOut

router = APIRouter()


# PUBLIC_INTERFACE
@router.post("", summary="Create product", response_model=ProductOut, dependencies=[Depends(require_roles("admin", "manager"))])
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    """This is a public function."""
    if db.query(Product).filter(Product.sku == payload.sku).first():
        raise HTTPException(status_code=400, detail="SKU already exists")
    prod = Product(**payload.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod


# PUBLIC_INTERFACE
@router.get("", summary="List products", response_model=List[ProductOut], dependencies=[Depends(require_roles("admin", "manager", "viewer"))])
def list_products(
    db: Session = Depends(get_db), q: str | None = Query(default=None, description="Search by name or SKU")
):
    """This is a public function."""
    query = db.query(Product)
    if q:
        like = f"%{q}%"
        query = query.filter((Product.name.ilike(like)) | (Product.sku.ilike(like)))
    return query.order_by(Product.id.desc()).all()


# PUBLIC_INTERFACE
@router.get("/{product_id}", summary="Get product", response_model=ProductOut, dependencies=[Depends(require_roles("admin", "manager", "viewer"))])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """This is a public function."""
    prod = db.get(Product, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Not found")
    return prod


# PUBLIC_INTERFACE
@router.patch("/{product_id}", summary="Update product", response_model=ProductOut, dependencies=[Depends(require_roles("admin", "manager"))])
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    """This is a public function."""
    prod = db.get(Product, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(prod, k, v)
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod


# PUBLIC_INTERFACE
@router.delete("/{product_id}", summary="Delete product", dependencies=[Depends(require_roles("admin"))])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """This is a public function."""
    prod = db.get(Product, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(prod)
    db.commit()
    return {"message": "deleted"}
