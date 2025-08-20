from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import require_roles
from ..models.inventory_item import InventoryItem
from ..models.product import Product

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/stock-summary", summary="Total stock per product", dependencies=[Depends(require_roles("admin", "manager", "viewer"))])
def stock_summary(db: Session = Depends(get_db)):
    """This is a public function."""
    rows = (
        db.query(Product.id, Product.sku, Product.name, func.sum(InventoryItem.quantity).label("total_qty"))
        .join(InventoryItem, InventoryItem.product_id == Product.id)
        .group_by(Product.id, Product.sku, Product.name)
        .all()
    )
    return [{"product_id": r.id, "sku": r.sku, "name": r.name, "total_quantity": int(r.total_qty or 0)} for r in rows]


# PUBLIC_INTERFACE
@router.get("/low-stock", summary="Products with low stock", dependencies=[Depends(require_roles("admin", "manager", "viewer"))])
def low_stock(threshold: int = 5, db: Session = Depends(get_db)):
    """This is a public function."""
    rows = (
        db.query(Product.id, Product.sku, Product.name, func.sum(InventoryItem.quantity).label("total_qty"))
        .join(InventoryItem, InventoryItem.product_id == Product.id)
        .group_by(Product.id, Product.sku, Product.name)
        .having(func.sum(InventoryItem.quantity) <= threshold)
        .all()
    )
    return [{"product_id": r.id, "sku": r.sku, "name": r.name, "total_quantity": int(r.total_qty or 0)} for r in rows]
