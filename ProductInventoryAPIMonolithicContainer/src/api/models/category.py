from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint

from ..core.db import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("name", name="uq_categories_name"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(String(512), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
