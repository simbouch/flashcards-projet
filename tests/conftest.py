"""
Pytest configuration for backend service tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
from datetime import datetime, timedelta

from src.main import app
from db_module.database import get_db, Base
import db_module.models  # Import all models to ensure they're registered with Base
from db_module import crud, schemas

# Create a test client
@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

# Create a test database session
@pytest.fixture
def test_db():
    """Get a test database session."""
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

# Override the dependency to use the test database
@pytest.fixture(autouse=True)
def db_override(monkeypatch, test_db):
    """Override the database dependency."""
    # Override the get_db dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    # Create all tables in the database
    from db_module.database import Base
    import db_module.models  # Import all models to ensure they're registered with Base

    # Get the engine from the test_db session
    engine = test_db.get_bind()

    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    # Create a test user in the database
    from db_module import crud, schemas
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="Password123",
        full_name="Test User"
    )

    # Check if user already exists
    existing_user = crud.get_user_by_email(test_db, user_data.email)
    if not existing_user:
        # Create new user
        crud.create_user(test_db, user_data)

    # Override both the database module's get_db and the API's get_db
    monkeypatch.setattr("db_module.database.get_db", override_get_db)
    monkeypatch.setattr("src.api.deps.get_db", override_get_db)

    # Also override the app's dependency directly
    from src.main import app
    from fastapi import Depends

    # Get the original route dependencies
    for route in app.routes:
        if hasattr(route, "dependencies"):
            # Replace any dependency that uses get_db with our test_db
            for i, dependency in enumerate(route.dependencies):
                if hasattr(dependency, "dependency") and dependency.dependency.__name__ == "get_db":
                    # Create a new dependency that uses our test_db
                    route.dependencies[i] = Depends(override_get_db)

    # Return the test_db for convenience
    return test_db

@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="Password123",
        full_name="Test User"
    )

    # Check if user already exists
    existing_user = crud.get_user_by_email(test_db, user_data.email)
    if existing_user:
        return existing_user

    # Create new user
    return crud.create_user(test_db, user_data)

@pytest.fixture
def test_refresh_token(test_db, test_user):
    """Create a test refresh token."""
    # Create a refresh token with default expiration
    return crud.create_refresh_token(test_db, test_user.id)
