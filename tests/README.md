# Flashcards Application Tests

This directory contains tests for the Flashcards application.

## Test Structure

The tests are organized as follows:

- `integration/`: Integration tests that test the entire application
  - `test_app_integration.py`: Tests the complete flow from uploading an image to generating flashcards
  - `images/`: Test images used by the integration tests

- `backend_service/tests/`: Tests for the backend service
  - `conftest.py`: Contains fixtures for the tests
  - `test_auth.py`: Tests for authentication endpoints
  - `test_refresh_token.py`: Tests for refresh token functionality

- `db_module/tests/`: Tests for the database module
  - `conftest.py`: Contains fixtures for the tests
  - `test_crud.py`: Tests for CRUD operations
  - `test_models.py`: Tests for database models

- `ocr_service/tests/`: Tests for the OCR service

- `llm_service/tests/`: Tests for the LLM service

## Running the Tests

### All Tests

To run all tests in the project:

```bash
python -m pytest
```

### Service-Specific Tests

To run tests for a specific service:

```bash
# Backend service tests
python -m pytest backend_service/tests

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
