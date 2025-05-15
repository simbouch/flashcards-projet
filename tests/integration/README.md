# Application Integration Tests

This directory contains integration tests for the entire Flashcards application. These tests verify that all services work together correctly.

## Test Files

- `test_app.py`: Tests for individual service health checks
- `test_app_integration.py`: Tests for the complete flow from uploading an image to generating flashcards

## Test Images

The `images/` directory contains test images used by the integration tests.

## Running Integration Tests

**Note**: These tests require all services to be running. They are meant to be run manually after starting all services.

To run all integration tests:

```bash
python -m pytest tests/integration
```

To run a specific integration test file:

```bash
python -m pytest tests/integration/test_app.py
python -m pytest tests/integration/test_app_integration.py
```

To run the tests as a script (with more detailed output):

```bash
python tests/integration/test_app.py
python tests/integration/test_app_integration.py
```
