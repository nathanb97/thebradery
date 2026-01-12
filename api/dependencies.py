"""FastAPI dependencies."""

from database import get_db

# Re-export database dependency for API use
__all__ = ['get_db']