from contextlib import contextmanager

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as SS
from sqlalchemy_utils import create_database, database_exists

import settings

Base = declarative_base()


class Settings(Base):

    __tablename__ = "settings"

    name = Column(String(100), primary_key=True)
    value = Column(String(100), nullable=True)
    status = Column(Boolean(), default=True)

    def __repr__(self):
        return f"<Settings name={self.name} value={self.value} status={self.status}>"


URI = (
    f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASS}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

if not database_exists(URI):
    create_database(URI, encoding="utf8mb4")

engine = create_engine(
    URI, pool_pre_ping=True, pool_recycle=3600, pool_size=20, max_overflow=40
)
Base.metadata.create_all(bind=engine)


def get_database() -> SS:
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        return session
    except:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def session_scope() -> SS:
    """Provide a transactional scope around a series of operations."""
    local_engine = create_engine(
        URI, pool_pre_ping=True, pool_recycle=3600, pool_size=20, max_overflow=40
    )
    Base.metadata.create_all(bind=local_engine)
    Session = sessionmaker(bind=local_engine)
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
