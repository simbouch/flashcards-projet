"""
Dependency injection for the API endpoints.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from db_module.database import get_db
from ..auth.jwt import get_current_user, get_current_active_user

# Re-export dependencies from other modules
# This allows endpoints to import all dependencies from a single module
__all__ = ["get_db", "get_current_user", "get_current_active_user"]
