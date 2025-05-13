# Flashcards Application Tests

This directory contains tests for the Flashcards application.

## Test Structure

The tests are organized as follows:

- `integration/`: Integration tests that test the entire application
  - `test_app_integration.py`: Tests the complete flow from uploading an image to generating flashcards
  - `images/`: Test images used by the integration tests

## Running the Tests

### Integration Tests

To run the integration tests, make sure all services are running:

```bash
docker-compose up -d
```

Then run the integration tests:

```bash
python -m tests.integration.test_app_integration
```

## Service-Specific Tests

Each service has its own tests in its respective directory:

- `ocr_service/tests/`: Tests for the OCR service
- `llm_service/tests/`: Tests for the LLM service
- `backend_service/tests/`: Tests for the backend service
- `db_module/tests/`: Tests for the database module

To run the tests for a specific service, navigate to the service directory and run:

```bash
python -m pytest
```

For example, to run the tests for the database module:

```bash
cd db_module
python -m pytest
```

## Test Coverage

To run the tests with coverage, use:

```bash
python -m pytest --cov=.
```

This will generate a coverage report showing which parts of the code are covered by tests.
