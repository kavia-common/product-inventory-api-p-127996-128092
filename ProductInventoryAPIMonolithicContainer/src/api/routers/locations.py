from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import require_roles
from ..models.location import Location
from ..schemas.location import LocationCreate, LocationUpdate, LocationOut

router = APIRouter()


# PUBLIC_INTERFACE
@router.post("", summary="Create location", response_model=LocationOut, dependencies=[Depends(require_roles("admin", "manager"))])
def create_location(payload: LocationCreate, db: Session = Depends(get_db)):
    """This is a public function."""
    if db.query(Location).filter(Location.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Location code exists")
    loc = Location(**payload.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


# PUBLIC_INTERFACE
@router.get("", summary="List locations", response_model=List[LocationOut], dependencies=[Depends(require_roles("admin", "manager", "viewer"))])
def list_locations(db: Session = Depends(get_db)):
    """This is a public function."""
    return db.query(Location).order_by(Location.id.desc()).all()


# PUBLIC_INTERFACE
@router.patch("/{location_id}", summary="Update location", response_model=LocationOut, dependencies=[Depends(require_roles("admin", "manager"))])
def update_location(location_id: int, payload: LocationUpdate, db: Session = Depends(get_db)):
    """This is a public function."""
    loc = db.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(loc, k, v)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


# PUBLIC_INTERFACE
@router.delete("/{location_id}", summary="Delete location", dependencies=[Depends(require_roles("admin"))])
def delete_location(location_id: int, db: Session = Depends(get_db)):
    """This is a public function."""
    loc = db.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(loc)
    db.commit()
    return {"message": "deleted"}
