from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, UniqueConstraint

from ..core.db import Base


class Webhook(Base):
    __tablename__ = "webhooks"
    __table_args__ = (UniqueConstraint("name", name="uq_webhooks_name"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    url = Column(String(512), nullable=False)
    secret = Column(String(256), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
