from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import require_roles
from ..models.inventory_item import InventoryItem
from ..models.location import Location
from ..models.product import Product
from ..schemas.inventory import InventoryCreate, InventoryUpdate, InventoryOut

router = APIRouter()


def _get_or_create_inventory(db: Session, product_id: int, location_id: int) -> InventoryItem:
    inv = db.query(InventoryItem).filter(
        InventoryItem.product_id == product_id, InventoryItem.location_id == location_id
    ).first()
    if not inv:
        inv = InventoryItem(product_id=product_id, location_id=location_id, quantity=0)
        db.add(inv)
        db.commit()
        db.refresh(inv)
    return inv


# PUBLIC_INTERFACE
@router.post("", summary="Create or set inventory record", response_model=InventoryOut, dependencies=[Depends(require_roles("admin", "manager"))])
def create_inventory(payload: InventoryCreate, db: Session = Depends(get_db)):
    """This is a public function."""
    if not db.get(Product, payload.product_id) or not db.get(Location, payload.location_id):
        raise HTTPException(status_code=400, detail="Invalid product or location")
    inv = _get_or_create_inventory(db, payload.product_id, payload.location_id)
    inv.quantity = payload.quantity
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


# PUBLIC_INTERFACE
@router.get("", summary="List inventory records", response_model=List[InventoryOut], dependencies=[Depends(require_roles("admin", "manager", "viewer"))])
def list_inventory(db: Session = Depends(get_db)):
    """This is a public function."""
    return db.query(InventoryItem).all()


# PUBLIC_INTERFACE
@router.patch("/{inventory_id}", summary="Update inventory quantity", response_model=InventoryOut, dependencies=[Depends(require_roles("admin", "manager"))])
def update_inventory(inventory_id: int, payload: InventoryUpdate, db: Session = Depends(get_db)):
    """This is a public function."""
    inv = db.get(InventoryItem, inventory_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Not found")
    inv.quantity = payload.quantity
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


# PUBLIC_INTERFACE
@router.post("/transfer", summary="Transfer quantity between locations", response_model=List[InventoryOut], dependencies=[Depends(require_roles("admin", "manager"))])
def transfer(product_id: int, from_location_id: int, to_location_id: int, quantity: int, db: Session = Depends(get_db)):
    """This is a public function."""
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    src = _get_or_create_inventory(db, product_id, from_location_id)
    dst = _get_or_create_inventory(db, product_id, to_location_id)
    if src.quantity < quantity:
        raise HTTPException(status_code=400, detail="Insufficient quantity")
    src.quantity -= quantity
    dst.quantity += quantity
    db.add_all([src, dst])
    db.commit()
    db.refresh(src)
    db.refresh(dst)
    return [src, dst]
