"""Database module - shared database configuration and connection."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config

print(f"Environment detected: IS_LOCAL={config.IS_LOCAL}")

# Toujours utiliser COMPUTED_DATABASE_URL qui gère déjà la logique
print(f"🔌 Database URL: {config.COMPUTED_DATABASE_URL}")

# Créer l'engine et session
engine = create_engine(config.COMPUTED_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables in the database."""
    Base.metadata.drop_all(bind=engine)