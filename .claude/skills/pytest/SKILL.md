---
name: pytest
description: "Comprehensive pytest testing support for Python projects with FastAPI focus. Use when: (1) Writing test files for existing code, (2) Running and debugging tests, (3) Need pytest best practices and patterns, (4) Testing FastAPI endpoints with TestClient, (5) Setting up test fixtures and parametrization, (6) Mocking dependencies, (7) Configuring pytest for a project, or any other pytest-related tasks."
---

# Pytest Testing

Comprehensive pytest support for writing, running, and debugging tests in Python projects, with specialized FastAPI testing patterns.

## Quick Start

### Generate Test Files

Use the test generation script to create test files from existing code:

```bash
# Generate test for a regular module
python scripts/generate_test.py app/models.py

# Generate test for FastAPI endpoints
python scripts/generate_test.py app/main.py --fastapi

# Specify custom output location
python scripts/generate_test.py app/utils.py --output tests/test_utils.py
```

The script analyzes your source code and generates pytest test templates with:
- Test functions for each function/method
- Test classes for each class
- FastAPI-specific tests for route handlers
- Fixture suggestions based on function parameters
- Parametrization templates for functions with arguments

### Set Up Test Environment

Copy configuration templates to your project:

```bash
# Copy pytest configuration
cp assets/pytest.ini ./pytest.ini

# Copy conftest.py template
cp assets/conftest.py ./tests/conftest.py

# Copy test template for reference
cp assets/test_template.py ./tests/test_template.py
```

Edit these files to match your project structure and requirements.

## Core Testing Workflows

### 1. Writing Tests

**For functions:**
```python
def test_calculate_total():
    # Arrange: Set up test data
    items = [{"price": 10}, {"price": 20}]

    # Act: Perform operation
    result = calculate_total(items)

    # Assert: Verify outcome
    assert result == 30
```

**For classes:**
```python
class TestUser:
    @pytest.fixture
    def user(self):
        return User(name="Alice", email="alice@example.com")

    def test_user_creation(self, user):
        assert user.name == "Alice"
        assert user.email == "alice@example.com"
```

**For FastAPI endpoints:**
```python
def test_create_item(client):
    response = client.post(
        "/items/",
        json={"name": "Test Item", "price": 10.99}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"
```

### 2. Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_user_creation

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_user"

# Run with coverage
pytest --cov=myapp --cov-report=html

# Stop after first failure
pytest -x

# Run only failed tests
pytest --lf
```

### 3. Debugging Failed Tests

```bash
# Show local variables on failure
pytest -l

# Show full diff on assertion failures
pytest -vv

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb
```

**In code:**
```python
def test_complex_operation():
    data = fetch_data()
    pytest.set_trace()  # Drop into pdb debugger here
    result = process(data)
    assert result is not None
```

## FastAPI Testing

For comprehensive FastAPI testing patterns, see [references/fastapi-testing.md](references/fastapi-testing.md).

**Key patterns covered:**

1. **Test Client Setup** - Configure TestClient and AsyncClient
2. **Dependency Overrides** - Override database, auth, and other dependencies
3. **Database Testing** - In-memory databases, transaction rollback, test data factories
4. **Authentication Testing** - JWT tokens, login flows, protected endpoints
5. **Async Testing** - Test async endpoints and background tasks
6. **File Uploads** - Test single and multiple file uploads
7. **WebSockets** - Test WebSocket connections and messages

**Quick example:**
```python
from fastapi.testclient import TestClient
from myapp.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_endpoint(client):
    response = client.get("/items")
    assert response.status_code == 200
```

## Pytest Patterns

For detailed pytest patterns and best practices, see [references/pytest-patterns.md](references/pytest-patterns.md).

**Topics covered:**

1. **Test Organization** - Directory structure, naming conventions, test classes
2. **Fixtures** - Scopes, dependencies, parametrized fixtures, autouse
3. **Parametrization** - Multiple test cases, complex scenarios, cartesian products
4. **Mocking and Patching** - Mock objects, patching functions/methods, side effects
5. **Markers** - Built-in markers (skip, xfail), custom markers, marker combinations
6. **Test Assertions** - Basic assertions, approximate comparisons, custom messages
7. **Exception Testing** - Testing expected exceptions and error messages
8. **Debugging Tests** - Print debugging, pytest.set_trace(), verbose output

**Common patterns:**

**Fixtures for test data:**
```python
@pytest.fixture
def user_data():
    return {"name": "Alice", "email": "alice@example.com"}

def test_create_user(user_data):
    user = User(**user_data)
    assert user.name == "Alice"
```

**Parametrization for multiple cases:**
```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

**Mocking external dependencies:**
```python
@patch('myapp.api.requests.get')
def test_fetch_data(mock_get):
    mock_get.return_value.json.return_value = {"status": "ok"}
    result = fetch_api_data()
    assert result["status"] == "ok"
```

## Configuration

### pytest.ini

The `assets/pytest.ini` template includes:

- Test discovery patterns
- Verbose output options
- Custom markers for organizing tests
- Coverage configuration
- Asyncio support
- Timeout settings
- Warning filters

Customize for your project needs.

### conftest.py

The `assets/conftest.py` template provides:

- Database fixtures (engine, session)
- FastAPI TestClient fixtures
- Authentication fixtures (test users, auth headers)
- Test data factories
- Mock fixtures for external APIs
- Automatic cleanup fixtures

Uncomment and customize the fixtures you need.

## Best Practices

### Test Isolation

Ensure tests don't share mutable state:

```python
# ❌ Bad: Shared mutable state
_cache = []

def test_adds_to_cache():
    _cache.append(1)
    assert len(_cache) == 1  # Fails if run after another test

# ✅ Good: Isolated state
@pytest.fixture
def cache():
    return []

def test_adds_to_cache(cache):
    cache.append(1)
    assert len(cache) == 1
```

### AAA Pattern

Structure tests with Arrange-Act-Assert:

```python
def test_user_creation():
    # Arrange: Set up test data
    name = "Alice"
    email = "alice@example.com"

    # Act: Perform the operation
    user = User(name=name, email=email)

    # Assert: Verify the outcome
    assert user.name == name
    assert user.email == email
```

### Descriptive Test Names

```python
# ✅ Good: Clear, specific
def test_user_creation_with_valid_email():
    pass

def test_user_creation_fails_with_invalid_email():
    pass

# ❌ Bad: Vague
def test_user():
    pass

def test_1():
    pass
```

### Use Markers

Organize tests with markers:

```python
@pytest.mark.slow
def test_expensive_operation():
    pass

@pytest.mark.integration
def test_full_workflow():
    pass

# Run specific markers
# pytest -m "not slow"
# pytest -m integration
```

## Resources

### scripts/generate_test.py

Python script to generate pytest test files from source code. Analyzes functions, classes, and FastAPI routes to create comprehensive test templates with fixtures and parametrization suggestions.

### references/fastapi-testing.md

Comprehensive guide for testing FastAPI applications covering TestClient setup, dependency overrides, database testing, authentication, async testing, file uploads, and WebSockets.

### references/pytest-patterns.md

Essential pytest patterns including test organization, fixtures, parametrization, mocking, markers, assertions, exception testing, and debugging techniques.

### assets/conftest.py

Template for shared pytest fixtures including database setup, FastAPI test client, authentication, test data factories, and mock fixtures.

### assets/pytest.ini

Template pytest configuration file with test discovery patterns, markers, coverage settings, and output options.

### assets/test_template.py

Comprehensive test file template demonstrating various testing patterns including fixtures, parametrization, mocking, async tests, and integration tests.
