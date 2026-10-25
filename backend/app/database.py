"""
Database connection setup.

Uses SQLite for the prototype (zero setup, single file, fast to iterate on).
Because we go through SQLAlchemy, switching to PostgreSQL later is a
one-line change: just replace DATABASE_URL below with something like
"postgresql://user:password@localhost/sih25033" and everything else
(models.py, main.py) stays exactly the same.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./sih25033.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # only needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
