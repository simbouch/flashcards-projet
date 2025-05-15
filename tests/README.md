# Flashcards Application Tests

This directory contains tests for the Flashcards application.

## Test Structure

The tests are organized as follows:

- `integration/`: Integration tests that test the entire application
  - `test_app_integration.py`: Tests the complete flow from uploading an image to generating flashcards
  - `images/`: Test images used by the integration tests

- `backend_service/tests/`: Tests for the backend service
  - `unit/`: Unit tests that mock dependencies and test individual components in isolation
  - `integration/`: Integration tests that test multiple components together
  - `conftest.py`: Contains fixtures for the tests
  - `test_auth.py`: Tests for authentication endpoints
  - `test_refresh_token.py`: Tests for refresh token functionality

- `db_module/tests/`: Tests for the database module
  - `conftest.py`: Contains fixtures for the tests
  - `test_crud.py`: Tests for CRUD operations
  - `test_models.py`: Tests for database models

- `ocr_service/tests/`: Tests for the OCR service

- `llm_service/tests/`: Tests for the LLM service

## Test Categories

Tests are categorized using pytest markers:

- `auth`: Tests related to authentication
- `decks`: Tests related to decks
- `flashcards`: Tests related to flashcards
- `study`: Tests related to study sessions
- `unit`: Unit tests that mock dependencies
- `integration`: Integration tests that test multiple components

## Running the Tests

### All Tests

To run all tests in the project:

```bash
python -m pytest
```

### Tests by Category

To run tests by category:

```bash
python -m pytest -m auth
python -m pytest -m decks
python -m pytest -m flashcards
python -m pytest -m study
python -m pytest -m unit
python -m pytest -m integration
```

### Service-Specific Tests

To run tests for a specific service:

```bash
# Backend service tests
python -m pytest backend_service/tests

# Backend service unit tests
python -m pytest backend_service/tests/unit

# Database module tests
python -m pytest db_module/tests

# OCR service tests
python -m pytest ocr_service/tests

# LLM service tests
python -m pytest llm_service/tests
```

### Integration Tests

To run the integration tests, make sure all services are running:

```bash
docker-compose up -d
```

Then run the integration tests:

```bash
python -m pytest tests/integration
```

## Test Coverage

To run the tests with coverage, use:

```bash
python -m pytest --cov=.
```

This will generate a coverage report showing which parts of the code are covered by tests.

## Testing Approach

The tests follow these best practices for testing FastAPI applications with SQLAlchemy:

1. **In-memory SQLite Database**: Tests use an in-memory SQLite database for speed and isolation.

2. **Session-per-test with Rollback**: Each test gets a fresh database session that is rolled back after the test completes, ensuring test isolation.

3. **Explicit Model Registration**: All models are explicitly imported to ensure they're registered with SQLAlchemy.

4. **Single Source of Truth for DB URL**: The test database URL is defined in a single place.

5. **Properly Scoped Fixtures**:
   - `scope="session"` for database setup/teardown
   - `scope="function"` for database sessions and test clients

6. **Dependency Overrides**: FastAPI's dependency injection system is overridden to use test fixtures.

## Common Issues and Solutions

### "No Such Table" Errors

If you encounter "no such table" errors:

1. Make sure all models are imported before calling `Base.metadata.create_all()`
2. Check that the database dependency is properly overridden
3. Verify that the test database is properly configured

Example of proper model imports:

```python
# Import all models explicitly to ensure they're registered with Base
import db_module.models
from db_module.models import User, Document, ExtractedText, Deck, Flashcard, RefreshToken, StudySession, StudyRecord
```

### Test Database Configuration

The tests use an in-memory SQLite database to ensure they don't affect the production database:

```python
# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create all tables in the database
Base.metadata.create_all(bind=engine)
```

### Dependency Overriding

The tests override the database dependency to use the test database:

```python
# Override the get_db dependency
def override_get_db():
    try:
        yield test_db
    finally:
        pass

# Override both the database module's get_db and the API's get_db
monkeypatch.setattr("db_module.database.get_db", override_get_db)
monkeypatch.setattr("backend_service.src.api.deps.get_db", override_get_db)
```
