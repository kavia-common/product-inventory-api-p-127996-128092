from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func, String

from ..core.db import Base


class Cost(Base):
    __tablename__ = "costs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    unit_cost = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    effective_at = Column(DateTime, server_default=func.now(), nullable=False)
