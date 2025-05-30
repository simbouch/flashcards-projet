# Backend Service Tests

This directory contains tests for the backend service of the Flashcards application.

## Test Structure

The tests are organized into the following directories:

- `unit/`: Unit tests that mock dependencies and test individual components in isolation
  - `test_auth_service.py`: Tests for authentication service functions
  - `test_deck_service.py`: Tests for deck service functions
  - `test_flashcard_service.py`: Tests for flashcard service functions

- `integration/`: Integration tests that test multiple components together
  - `test_flashcards.py`: Tests for flashcard generation flow

- `conftest.py`: Pytest configuration and fixtures for the tests
- `test_auth.py`: Tests for authentication endpoints
- `test_refresh_token.py`: Tests for refresh token functionality

## Test Categories

Tests are categorized using pytest markers:

- `auth`: Tests related to authentication
- `decks`: Tests related to decks
- `flashcards`: Tests related to flashcards
- `study`: Tests related to study sessions
- `unit`: Unit tests that mock dependencies
- `integration`: Integration tests that test multiple components

## Issues and Solutions

### Database Table Creation

The main issue with the tests is that the database tables aren't being created properly in the test environment. This is because the SQLAlchemy models need to be imported and registered with the Base metadata before creating the tables.

To fix this issue:

1. Make sure all models are imported before calling `Base.metadata.create_all()`
2. Use a single test database session for all tests
3. Create the tables before running the tests

### Test Database Configuration

The test database should be configured to use an in-memory SQLite database for tests. This ensures that the tests are isolated and don't affect the production database.

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

The tests need to override the database dependency to use the test database instead of the production database. This is done using the `monkeypatch` fixture:

```python
@pytest.fixture(autouse=True)
def db_override(monkeypatch, test_db):
    """Override the database dependency."""
    # Import all models to ensure they're registered with Base
    # These imports are necessary for SQLAlchemy to register the models with Base.metadata
    # even if they're not directly used in the code (ignore linter warnings)
    from db_module.database import Base
    import db_module.models
    from db_module.models import User, Document, ExtractedText, Deck, Flashcard, RefreshToken, StudySession, StudyRecord

    # Get the engine from the test_db session
    engine = test_db.get_bind()

    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

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

## Running the Tests

To run all tests:

```bash
python -m pytest
```

To run tests by category:

```bash
python -m pytest -m auth
python -m pytest -m decks
python -m pytest -m flashcards
python -m pytest -m study
python -m pytest -m unit
python -m pytest -m integration
```

To run tests by directory:

```bash
python -m pytest backend_service/tests/unit
python -m pytest backend_service/tests/integration
```

## Troubleshooting

If you encounter issues with the tests, check the following:

1. Make sure all models are imported before calling `Base.metadata.create_all()`
2. Check that the database dependency is properly overridden
3. Verify that the test database is properly configured
4. Ensure that the fixtures are properly set up
