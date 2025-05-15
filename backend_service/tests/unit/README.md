# Unit Tests

This directory contains unit tests for the backend service. Unit tests focus on testing individual components in isolation, mocking any dependencies.

## Test Files

- `test_auth_service.py`: Tests for the authentication service

## Writing Unit Tests

When writing unit tests:

1. Use the `@pytest.mark.unit` marker to categorize the test as a unit test
2. Use mocks to isolate the component being tested
3. Follow the AAA (Arrange-Act-Assert) pattern
4. Use descriptive test names and docstrings

## Example

```python
@pytest.mark.auth
@pytest.mark.unit
def test_create_access_token():
    """Test creating an access token."""
    # Arrange
    user_id = 1
    expires_delta = timedelta(minutes=15)
    
    # Act
    token = create_access_token({"sub": str(user_id)}, expires_delta)
    
    # Assert
    assert token is not None
    assert isinstance(token, str)
```

## Running Unit Tests

To run all unit tests:

```bash
python -m pytest backend_service/tests/unit
```

To run a specific unit test file:

```bash
python -m pytest backend_service/tests/unit/test_auth_service.py
```

To run a specific unit test:

```bash
python -m pytest backend_service/tests/unit/test_auth_service.py::test_create_access_token
```
