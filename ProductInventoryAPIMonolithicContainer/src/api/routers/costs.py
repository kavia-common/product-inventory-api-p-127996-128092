from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import require_roles
from ..models.cost import Cost
from ..models.product import Product
from ..schemas.cost import CostCreate, CostOut

router = APIRouter()


# PUBLIC_INTERFACE
@router.post("", summary="Create cost record", response_model=CostOut, dependencies=[Depends(require_roles("admin", "manager"))])
def create_cost(payload: CostCreate, db: Session = Depends(get_db)):
    """This is a public function."""
    if not db.get(Product, payload.product_id):
        raise HTTPException(status_code=400, detail="Invalid product")
    c = Cost(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# PUBLIC_INTERFACE
@router.get("", summary="List costs", response_model=List[CostOut], dependencies=[Depends(require_roles("admin", "manager", "viewer"))])
def list_costs(product_id: int | None = None, db: Session = Depends(get_db)):
    """This is a public function."""
    q = db.query(Cost)
    if product_id:
        q = q.filter(Cost.product_id == product_id)
    return q.order_by(Cost.id.desc()).all()
