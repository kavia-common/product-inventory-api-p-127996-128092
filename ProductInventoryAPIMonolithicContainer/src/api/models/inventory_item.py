from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.db import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    __table_args__ = (UniqueConstraint("product_id", "location_id", name="uq_inventory_product_location"),)

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    product = relationship("Product")
    location = relationship("Location")
