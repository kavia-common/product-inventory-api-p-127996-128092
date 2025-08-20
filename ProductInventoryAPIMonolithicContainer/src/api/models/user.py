from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from ..core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(256), unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(32), nullable=False, default="manager")  # admin, manager, viewer
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
