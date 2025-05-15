# Test Structure Improvements

This document outlines the improvements made to the test structure of the Flashcards application.

## Overview of Changes

1. **Organized Test Directory Structure**
   - Created proper `unit/` and `integration/` subdirectories
   - Added README.md files to document each directory's purpose
   - Ensured consistent structure across test directories

2. **Removed Duplicate Tests**
   - Identified duplicate tests between `tests/` and `backend_service/tests/`
   - Kept the tests in `backend_service/tests/` as the primary tests
   - Updated the tests in `tests/` to be stubs that reference the primary tests

3. **Added Test Markers**
   - Added pytest markers to categorize tests by functionality and type
   - Updated pytest.ini to include marker definitions
   - Applied markers consistently across test files

4. **Fixed Test Issues**
   - Resolved circular import issues
   - Fixed database session handling
   - Ensured all tests pass with proper isolation

5. **Improved Documentation**
   - Updated the main README.md with test structure information
   - Added detailed README.md files to each test directory
   - Created a comprehensive testing guide

## Directory Structure

The test structure is now organized as follows:

```
tests/                           # Application-level tests
├── integration/                 # Integration tests for the entire application
│   ├── images/                  # Test images for integration tests
│   ├── test_app.py              # Tests for individual service health checks
│   ├── test_app_integration.py  # Tests for the complete application flow
│   └── README.md                # Documentation for integration tests
├── unit/                        # Unit tests for application components
│   └── README.md                # Documentation for unit tests
├── conftest.py                  # Shared test fixtures and configuration
├── test_auth.py                 # Authentication tests (references backend_service)
├── test_refresh_token.py        # Refresh token tests (references backend_service)
└── README.md                    # Documentation for application-level tests

backend_service/tests/           # Backend service tests
├── integration/                 # Integration tests for backend service
│   ├── test_flashcards.py       # Tests for flashcard functionality
│   └── README.md                # Documentation for backend integration tests
├── unit/                        # Unit tests for backend service
│   ├── conftest.py              # Unit test fixtures
│   ├── test_auth_service.py     # Tests for authentication service
│   └── README.md                # Documentation for unit tests
├── conftest.py                  # Shared test fixtures and configuration
├── test_auth.py                 # Authentication endpoint tests
├── test_refresh_token.py        # Refresh token functionality tests
├── README.md                    # Documentation for backend service tests
└── TESTING_GUIDE.md             # Comprehensive testing guide
```

## Test Categories

Tests are now categorized using pytest markers:

- `auth`: Tests related to authentication
- `decks`: Tests related to decks
- `flashcards`: Tests related to flashcards
- `study`: Tests related to study sessions
- `unit`: Unit tests that mock dependencies
- `integration`: Integration tests that test multiple components

## Running Tests

Tests can now be run in various ways:

```bash
# Run all tests
pytest

# Run tests by category
pytest -m auth
pytest -m decks
pytest -m flashcards
pytest -m study
pytest -m unit
pytest -m integration

# Run tests for specific services
pytest backend_service/tests
pytest db_module/tests
pytest ocr_service/tests
pytest llm_service/tests

# Run specific test directories
pytest backend_service/tests/unit
pytest backend_service/tests/integration
```

## Best Practices Implemented

1. **In-memory SQLite Database**: Tests use an in-memory SQLite database for speed and isolation.

2. **Session-per-test with Rollback**: Each test gets a fresh database session that is rolled back after the test completes, ensuring test isolation.

3. **Explicit Model Registration**: All models are explicitly imported to ensure they're registered with SQLAlchemy.

4. **Single Source of Truth for DB URL**: The test database URL is defined in a single place.

5. **Properly Scoped Fixtures**:
   - `scope="session"` for database setup/teardown
   - `scope="function"` for database sessions and test clients

6. **Dependency Overrides**: FastAPI's dependency injection system is overridden to use test fixtures.

## Future Improvements

1. **Address Deprecation Warnings**:
   - Update the code to address the deprecation warnings from Pydantic and SQLAlchemy
   - Replace `datetime.utcnow()` with `datetime.now(datetime.UTC)`
   - Update FastAPI event handlers to use lifespan events

2. **Add More Tests**:
   - Add more unit tests for other components
   - Add more integration tests for end-to-end functionality

3. **Improve Test Coverage**:
   - Add tests for edge cases and error conditions
   - Implement property-based testing for complex logic

4. **Set Up Continuous Integration**:
   - Set up CI/CD pipelines to run tests automatically
   - Add code coverage reporting
