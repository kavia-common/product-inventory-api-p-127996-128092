from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint

from ..core.db import Base


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = (UniqueConstraint("code", name="uq_locations_code"),)

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), nullable=False)  # warehouse code
    name = Column(String(128), nullable=False)
    address = Column(String(512), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
