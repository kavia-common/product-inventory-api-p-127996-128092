from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from .config import get_settings

Base = declarative_base()

_engine = None
_SessionLocal = None


def init_db() -> None:
    """Initialize database engine and session factory."""
    global _engine, _SessionLocal
    settings = get_settings()
    _engine = create_engine(settings.database_url(), echo=settings.SQL_ECHO, pool_pre_ping=True, pool_recycle=3600)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    # Import models to register with Base metadata
    from ..models import all_models  # noqa: F401
    Base.metadata.create_all(bind=_engine)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """This is a public function."""
    if _SessionLocal is None:
        init_db()
    db: Session = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
