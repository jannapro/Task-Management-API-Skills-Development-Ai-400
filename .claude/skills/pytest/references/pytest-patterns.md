# Pytest Patterns and Best Practices

Essential pytest patterns for writing effective tests.

## Table of Contents

1. [Test Organization](#test-organization)
2. [Fixtures](#fixtures)
3. [Parametrization](#parametrization)
4. [Mocking and Patching](#mocking-and-patching)
5. [Markers](#markers)
6. [Test Assertions](#test-assertions)
7. [Exception Testing](#exception-testing)
8. [Debugging Tests](#debugging-tests)

## Test Organization

### Directory Structure

```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── models.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_models.py       # Mirror src structure
│   ├── test_utils.py
│   └── integration/
│       └── test_api.py
└── pytest.ini
```

### Test Naming Conventions

```python
# Test files: test_*.py or *_test.py
# Test functions: test_*
# Test classes: Test*

def test_user_creation():
    """Good: Clear, descriptive name."""
    pass

def test_valid_email_format():
    """Good: Specific behavior being tested."""
    pass

def test_1():
    """Bad: Non-descriptive."""
    pass
```

### Test Class Organization

```python
class TestUserModel:
    """Group related tests in a class."""

    def test_create_user(self):
        user = User(name="Alice")
        assert user.name == "Alice"

    def test_user_validation(self):
        with pytest.raises(ValueError):
            User(name="")

    class TestUserMethods:
        """Nested class for specific method tests."""

        def test_get_full_name(self):
            user = User(first="Alice", last="Smith")
            assert user.get_full_name() == "Alice Smith"
```

## Fixtures

### Basic Fixtures

```python
import pytest

@pytest.fixture
def sample_user():
    """Simple fixture returning data."""
    return {"name": "Alice", "age": 30}

def test_user_data(sample_user):
    assert sample_user["name"] == "Alice"
```

### Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default: per test
def function_scope():
    return "recreated each test"

@pytest.fixture(scope="class")  # Per test class
def class_scope():
    return "shared within class"

@pytest.fixture(scope="module")  # Per test file
def module_scope():
    return "shared within module"

@pytest.fixture(scope="session")  # Once per test session
def session_scope():
    return "shared across all tests"
```

### Setup and Teardown

```python
@pytest.fixture
def database_connection():
    """Fixture with setup and teardown."""
    # Setup
    db = connect_to_database()

    yield db  # Test runs here

    # Teardown
    db.close()
```

### Fixture Dependencies

```python
@pytest.fixture
def database():
    return Database()

@pytest.fixture
def user_repo(database):
    """Fixture depending on another fixture."""
    return UserRepository(database)

def test_create_user(user_repo):
    user = user_repo.create("Alice")
    assert user.name == "Alice"
```

### Parametrized Fixtures

```python
@pytest.fixture(params=[1, 2, 3])
def number(request):
    """Runs test with each parameter."""
    return request.param

def test_number_positive(number):
    """Runs 3 times with different values."""
    assert number > 0
```

### Autouse Fixtures

```python
@pytest.fixture(autouse=True)
def reset_state():
    """Runs automatically for every test."""
    global_state.reset()
    yield
    global_state.clear()
```

## Parametrization

### Basic Parametrization

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (10, 20, 30),
    (-1, 1, 0),
])
def test_addition(a, b, expected):
    assert a + b == expected
```

### Parametrize with IDs

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
], ids=["two", "three", "four"])
def test_square_with_ids(input, expected):
    assert input ** 2 == expected
```

### Complex Parametrization

```python
@pytest.mark.parametrize("user_data,should_pass", [
    ({"name": "Alice", "email": "alice@example.com"}, True),
    ({"name": "", "email": "alice@example.com"}, False),
    ({"name": "Alice", "email": "invalid"}, False),
], ids=["valid", "empty_name", "invalid_email"])
def test_user_validation(user_data, should_pass):
    if should_pass:
        user = User(**user_data)
        assert user.name == user_data["name"]
    else:
        with pytest.raises(ValueError):
            User(**user_data)
```

### Cartesian Product

```python
@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", [10, 20])
def test_combinations(x, y):
    """Runs 6 times: all combinations of x and y."""
    assert x + y > 0
```

## Mocking and Patching

### Basic Mocking

```python
from unittest.mock import Mock

def test_with_mock():
    mock_obj = Mock()
    mock_obj.method.return_value = 42

    result = mock_obj.method()
    assert result == 42
    mock_obj.method.assert_called_once()
```

### Patching Functions

```python
from unittest.mock import patch

@patch('myapp.external_api.fetch_data')
def test_fetch_data(mock_fetch):
    mock_fetch.return_value = {"data": "mocked"}

    result = process_external_data()
    assert result["data"] == "mocked"
    mock_fetch.assert_called_once()
```

### Patching Methods

```python
@patch.object(User, 'save')
def test_user_save(mock_save):
    user = User(name="Alice")
    user.save()

    mock_save.assert_called_once()
```

### Context Manager Patching

```python
def test_with_context_patch():
    with patch('myapp.api.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}

        response = fetch_api_data()
        assert response["status"] == "ok"
```

### Mock Side Effects

```python
def test_side_effects():
    mock = Mock()
    mock.side_effect = [1, 2, 3]

    assert mock() == 1
    assert mock() == 2
    assert mock() == 3
```

### Mocking Exceptions

```python
@patch('myapp.database.query')
def test_database_error(mock_query):
    mock_query.side_effect = DatabaseError("Connection failed")

    with pytest.raises(DatabaseError):
        fetch_users()
```

### Spy Pattern (wraps)

```python
from myapp.utils import expensive_function

@patch('myapp.utils.expensive_function', wraps=expensive_function)
def test_function_called(mock_func):
    """Track calls while using real implementation."""
    result = process_data()

    mock_func.assert_called_once_with(expected_arg)
    assert result is not None
```

## Markers

### Built-in Markers

```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python 3.8+")
def test_new_python_feature():
    pass

@pytest.mark.xfail(reason="Known bug")
def test_known_issue():
    assert False  # Expected to fail
```

### Custom Markers

```python
# pytest.ini
[pytest]
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests

# Test file
@pytest.mark.slow
def test_slow_operation():
    time.sleep(2)

@pytest.mark.integration
def test_api_integration():
    pass

# Run specific markers
# pytest -m slow
# pytest -m "not slow"
# pytest -m "integration and not slow"
```

### Combining Markers

```python
@pytest.mark.slow
@pytest.mark.integration
def test_full_system():
    pass
```

## Test Assertions

### Basic Assertions

```python
def test_assertions():
    assert 1 + 1 == 2
    assert "hello" in "hello world"
    assert [1, 2, 3] == [1, 2, 3]
    assert {"key": "value"} == {"key": "value"}
```

### Approximate Comparisons

```python
def test_approximate():
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert {"a": 0.1 + 0.2} == {"a": pytest.approx(0.3)}
```

### Advanced Assertions

```python
def test_assertions_with_messages():
    value = calculate_result()
    assert value > 0, f"Expected positive, got {value}"

def test_type_checking():
    result = get_user()
    assert isinstance(result, User)

def test_collection_contains():
    users = get_all_users()
    assert any(u.name == "Alice" for u in users)
```

## Exception Testing

### Basic Exception Testing

```python
def test_exception():
    with pytest.raises(ValueError):
        int("not a number")
```

### Exception Message Testing

```python
def test_exception_message():
    with pytest.raises(ValueError, match="invalid literal"):
        int("not a number")
```

### Capturing Exception Details

```python
def test_exception_details():
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("Custom error message")

    assert "Custom error" in str(exc_info.value)
    assert exc_info.type is ValueError
```

### Testing No Exception

```python
def test_no_exception():
    """Verify function doesn't raise."""
    try:
        result = safe_operation()
        assert result is not None
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
```

## Debugging Tests

### Print Debugging

```python
def test_with_prints():
    data = {"key": "value"}
    print(f"Data: {data}")  # Shows in output with pytest -s
    assert "key" in data
```

### Using pytest.set_trace()

```python
def test_with_debugger():
    data = process_data()
    pytest.set_trace()  # Drops into pdb debugger
    assert data is not None
```

### Verbose Output

```bash
# Show print statements
pytest -s

# Verbose test output
pytest -v

# Show local variables on failure
pytest -l

# Full diff on assertion failure
pytest -vv
```

### Running Specific Tests

```bash
# Run specific file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_user_creation

# Run specific test in class
pytest tests/test_models.py::TestUser::test_creation

# Run tests matching pattern
pytest -k "test_user"
```

### Useful Flags

```bash
# Stop after first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show slowest tests
pytest --durations=10

# Run last failed tests
pytest --lf

# Run failed tests first
pytest --ff
```

## Test Isolation Best Practices

```python
# ❌ Bad: Shared mutable state
_global_cache = []

def test_adds_to_cache():
    _global_cache.append(1)
    assert len(_global_cache) == 1  # Fails if run after another test

# ✅ Good: Isolated state
@pytest.fixture
def cache():
    return []

def test_adds_to_cache(cache):
    cache.append(1)
    assert len(cache) == 1
```

## AAA Pattern (Arrange-Act-Assert)

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
