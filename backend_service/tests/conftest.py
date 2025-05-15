"""
Pytest configuration for backend service tests.

This module implements best practices for testing FastAPI applications with SQLAlchemy:
1. Centralizes model registration
2. Uses a single test database configuration
3. Creates/tears down tables exactly once per session
4. Provides a fresh, rollback-wrapped session per test
5. Properly overrides FastAPI's get_db dependency
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from backend_service.src.main import app
from db_module.database import get_db
# Import the centralized Base that includes all models
from db_module.base import Base
from db_module import crud, schemas

# Define a single test database URL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create a single engine for all tests
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    # Uncomment to see SQL statements for debugging
    # echo=True
)

# Create a sessionmaker for test sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Print registered tables for debugging
print("Registered tables:", Base.metadata.tables.keys())

@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    """Create all tables once at the beginning of the test session.

    This fixture runs automatically and ensures tables are created exactly once.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield

    # Drop all tables at the end of the test session
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(prepare_database):
    """Yield a fresh database session for each test.

    This fixture creates a new transaction for each test and rolls it back
    after the test completes, ensuring test isolation.
    """
    # Connect to the engine
    connection = engine.connect()
    # Begin a transaction
    transaction = connection.begin()
    # Create a session bound to this connection
    session = TestingSessionLocal(bind=connection)

    yield session

    # Close and rollback after the test
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with dependency overrides.

    This fixture overrides the get_db dependency to use our test session.
    """
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Set the override before creating the client
    app.dependency_overrides[get_db] = override_get_db

    # Create and yield the client
    with TestClient(app) as test_client:
        yield test_client

    # Clear the override after the test
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="Password123",
        full_name="Test User"
    )

    # Check if user already exists to avoid duplicate key errors
    existing_user = crud.get_user_by_email(db_session, user_data.email)
    if existing_user:
        return existing_user

    # Create new user
    user = crud.create_user(db_session, user_data)
    return user

@pytest.fixture
def test_refresh_token(db_session, test_user):
    """Create a test refresh token."""
    # Create a refresh token with 7 days expiration
    expires_delta = timedelta(days=7)
    db_refresh_token = crud.create_refresh_token(db_session, test_user.id, expires_delta)
    return db_refresh_token
