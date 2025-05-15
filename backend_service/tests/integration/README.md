# Integration Tests

This directory contains integration tests for the backend service. Integration tests verify that multiple components work together correctly.

## Test Files

- `test_flashcards.py`: Tests for the flashcard generation flow

## Running Integration Tests

To run all integration tests:

```bash
python -m pytest backend_service/tests/integration
```

To run a specific integration test file:

```bash
python -m pytest backend_service/tests/integration/test_flashcards.py
```
