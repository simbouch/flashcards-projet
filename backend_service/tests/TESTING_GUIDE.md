# Backend Service Testing Guide

This document provides guidance on running tests for the backend service and explains the test structure and best practices.

## Test Structure

The tests are organized as follows:

- `backend_service/tests/`: Root directory for all backend service tests
  - `conftest.py`: Contains shared fixtures for all tests
  - `test_auth.py`: Tests for authentication endpoints
  - `test_refresh_token.py`: Tests for refresh token functionality
  - `unit/`: Unit tests that mock dependencies
    - `test_auth_service.py`: Tests for authentication service
    - `test_deck_service.py`: Tests for deck service
    - `test_flashcard_service.py`: Tests for flashcard service
  - `integration/`: Integration tests that test multiple components
    - `test_flashcards.py`: Tests for flashcard functionality

## Running Tests

To run all tests:

```bash
python -m pytest
```

To run specific test files:

```bash
python -m pytest tests/test_auth.py
python -m pytest tests/test_refresh_token.py
```

To run tests by category:

```bash
# Run only unit tests
python -m pytest tests/unit/

# Run only integration tests
python -m pytest tests/integration/

# Run tests with specific markers
python -m pytest -m "auth"
```

## Test Database Configuration

The tests use an in-memory SQLite database to ensure they don't affect the production database. This is configured in the `conftest.py` file:

```python
# Define a single test database URL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create a single engine for all tests
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
```

## Best Practices

### 1. Centralized Model Registration

All models are registered in a central location (`db_module/base.py`) to ensure they're properly registered with SQLAlchemy's metadata:

```python
from db_module.database import Base
from db_module.models import (
    User, Document, ExtractedText, Deck, Flashcard,
    RefreshToken, StudySession, StudyRecord
)
```

### 2. Session-Scoped Database Setup

Tables are created once at the beginning of the test session and dropped at the end:

```python
@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    """Create all tables once at the beginning of the test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
```

### 3. Function-Scoped Database Sessions

Each test gets a fresh database session with transaction rollback:

```python
@pytest.fixture(scope="function")
def db_session(prepare_database):
    """Yield a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### 4. Dependency Overriding

The tests override FastAPI's dependency injection system to use the test database:

```python
@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with dependency overrides."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
```

## Common Issues and Solutions

### "No Such Table" Errors

If you encounter "no such table" errors:

1. **Model Registration**: Make sure all models are imported before calling `Base.metadata.create_all()`. Use the centralized model registration in `db_module/base.py`.

2. **Single Test Database**: Use a single test database configuration across all test files.

3. **Dependency Overriding**: Ensure the dependency overriding mechanism is consistently applied.

4. **Table Creation Timing**: Make sure tables are created before running tests.

### Duplicate Key Errors

If you encounter duplicate key errors when creating test users:

1. Check if the user already exists before creating a new one:

```python
existing_user = crud.get_user_by_email(db_session, user_data.email)
if existing_user:
    return existing_user
```

## Debugging Tips

1. **Print Registered Tables**: Add this line to see which tables are registered:

```python
print("Registered tables:", Base.metadata.tables.keys())
```

2. **Enable SQL Echo**: Uncomment this line in `conftest.py` to see SQL statements:

```python
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    # Uncomment to see SQL statements for debugging
    echo=True
)
```

## Test Refactoring Recommendations

1. **Use Transactions for Test Isolation**: Each test should run in its own transaction that gets rolled back after the test completes.

2. **Avoid Test Interdependence**: Tests should not depend on the state created by other tests.

3. **Mock External Services**: Use mocks for external services like OCR and LLM services.

4. **Use Fixtures Wisely**: Create fixtures for common test data and operations.

5. **Follow AAA Pattern**: Arrange, Act, Assert - structure your tests in this way for clarity.

## Addressing Deprecation Warnings

The codebase has been updated to address several deprecation warnings:

1. **Pydantic Validators**: Updated from `@validator` to `@field_validator` with `@classmethod` decorator:

```python
# Old approach
@validator('username')
def username_alphanumeric(cls, v):
    # validation logic
    return v

# New approach
@field_validator('username')
@classmethod
def username_alphanumeric(cls, v):
    # validation logic
    return v
```

2. **FastAPI Event Handlers**: Updated from `@app.on_event` to lifespan events:

```python
# Old approach
@app.on_event("startup")
async def startup_event():
    # startup logic

# New approach
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic
    yield
    # shutdown logic

app = FastAPI(lifespan=lifespan)
```

3. **SQLAlchemy Imports**: Updated to use `declarative_base` from `sqlalchemy.orm`:

```python
# Old approach
from sqlalchemy.ext.declarative import declarative_base

# New approach
from sqlalchemy.orm import declarative_base
```

4. **Datetime UTC Functions**: Updated from `datetime.utcnow()` to `datetime.now(UTC)`:

```python
# Old approach
expire = datetime.utcnow() + expires_delta

# New approach
expire = datetime.now(UTC) + expires_delta
```

## Conclusion

By following these best practices, you can ensure that your tests are reliable, isolated, and maintainable. The key is to have a consistent approach to database setup, model registration, and dependency overriding.
