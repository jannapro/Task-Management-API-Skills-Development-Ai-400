# Testing FastAPI Applications

## Overview

FastAPI makes testing easy with built-in test client support. This guide covers unit testing, integration testing, and test best practices.

## Setup

### Installation

```bash
pip install pytest
pip install httpx  # Required for TestClient
```

### Project Structure

```
project/
├── app/
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Shared fixtures
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_items.py
└── main.py
```

## Basic Testing

### Test Client

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with output
pytest -v

# Run specific test file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::test_create_user

# Run with coverage
pytest --cov=app --cov-report=html
```

## Database Testing

### Test Database Setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Using Fixtures

```python
# tests/test_users.py
def test_create_user(client):
    """Test creating a new user."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_get_user(client, db):
    """Test getting a user."""
    # Create a user first
    from app.crud import user as crud_user
    from app.schemas.user import UserCreate

    user = crud_user.create_user(
        db,
        UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
    )

    # Get the user
    response = client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

## Authentication Testing

### Helper Fixtures

```python
# tests/conftest.py
@pytest.fixture
def test_user(db):
    """Create a test user."""
    from app.crud import user as crud_user
    from app.schemas.user import UserCreate

    return crud_user.create_user(
        db,
        UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
    )

@pytest.fixture
def test_superuser(db):
    """Create a test superuser."""
    from app.crud import user as crud_user
    from app.schemas.user import UserCreate

    return crud_user.create_user(
        db,
        UserCreate(
            email="admin@example.com",
            username="admin",
            password="adminpass123",
            is_superuser=True
        )
    )

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Testing Protected Endpoints

```python
def test_read_users_me(client, auth_headers):
    """Test getting current user info."""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

def test_read_users_me_unauthorized(client):
    """Test that accessing /me without token fails."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
```

## Testing Different Scenarios

### Test Success Cases

```python
def test_create_user_success(client):
    """Test successful user creation."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
```

### Test Validation Errors

```python
def test_create_user_invalid_email(client):
    """Test that invalid email is rejected."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "not-an-email",
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 422  # Validation error

def test_create_user_missing_field(client):
    """Test that missing required field is rejected."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "test@example.com"
            # Missing username and password
        }
    )
    assert response.status_code == 422
```

### Test Error Cases

```python
def test_get_nonexistent_user(client):
    """Test getting a user that doesn't exist."""
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404

def test_create_duplicate_user(client):
    """Test that creating duplicate user fails."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }

    # Create first user
    response1 = client.post("/api/v1/users", json=user_data)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = client.post("/api/v1/users", json=user_data)
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"].lower()
```

### Test Authorization

```python
def test_admin_only_endpoint(client, auth_headers):
    """Test that regular users can't access admin endpoints."""
    response = client.get("/api/v1/admin/users", headers=auth_headers)
    assert response.status_code == 403  # Forbidden

def test_admin_only_endpoint_as_admin(client, test_superuser):
    """Test that superusers can access admin endpoints."""
    # Login as superuser
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@example.com",
            "password": "adminpass123"
        }
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Access admin endpoint
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200
```

## Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("email,username,expected_status", [
    ("valid@example.com", "validuser", 201),
    ("invalid-email", "user", 422),
    ("", "user", 422),
    ("valid@example.com", "", 422),
])
def test_create_user_variations(client, email, username, expected_status):
    """Test user creation with various inputs."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "username": username,
            "password": "password123"
        }
    )
    assert response.status_code == expected_status
```

## Mocking External Services

### Mock Email Service

```python
from unittest.mock import Mock, patch

@patch('app.services.email.send_email')
def test_registration_sends_email(mock_send_email, client):
    """Test that registration sends a welcome email."""
    mock_send_email.return_value = True

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )

    assert response.status_code == 201
    mock_send_email.assert_called_once()
```

## Test Coverage

### Generate Coverage Report

```bash
# Install coverage tool
pip install pytest-cov

# Run with coverage
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = app
omit =
    */tests/*
    */migrations/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Testing Best Practices

### 1. Follow AAA Pattern

```python
def test_create_user(client):
    # Arrange - Set up test data
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }

    # Act - Perform the action
    response = client.post("/api/v1/users", json=user_data)

    # Assert - Check the results
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
```

### 2. Use Descriptive Test Names

```python
# ✅ Good
def test_create_user_with_valid_data_returns_201():
    pass

def test_create_user_with_duplicate_email_returns_400():
    pass

# ❌ Bad
def test_1():
    pass

def test_user():
    pass
```

### 3. Test One Thing Per Test

```python
# ✅ Good - Each test has one responsibility
def test_create_user_success(client):
    response = client.post("/api/v1/users", json={"..."})
    assert response.status_code == 201

def test_create_user_returns_correct_data(client):
    response = client.post("/api/v1/users", json={"..."})
    assert response.json()["email"] == "test@example.com"

# ❌ Bad - Testing multiple things
def test_create_user(client):
    response = client.post("/api/v1/users", json={"..."})
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert "password" not in response.json()
    # ... many more assertions
```

### 4. Use Fixtures for Common Setup

```python
# tests/conftest.py
@pytest.fixture
def sample_users(db):
    """Create multiple sample users for testing."""
    from app.crud import user as crud_user
    from app.schemas.user import UserCreate

    users = []
    for i in range(5):
        user = crud_user.create_user(
            db,
            UserCreate(
                email=f"user{i}@example.com",
                username=f"user{i}",
                password="password123"
            )
        )
        users.append(user)
    return users

# tests/test_users.py
def test_list_users(client, sample_users):
    """Test listing users with pagination."""
    response = client.get("/api/v1/users?limit=3")
    assert response.status_code == 200
    assert len(response.json()) == 3
```

### 5. Clean Up After Tests

```python
@pytest.fixture(scope="function")
def db():
    """Create fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Clean up
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Common Testing Patterns

### Test Data Factories

```python
# tests/factories.py
from app.schemas.user import UserCreate

class UserFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
        defaults.update(kwargs)
        return UserCreate(**defaults)

# Usage
def test_create_user(client):
    user_data = UserFactory.create(email="custom@example.com")
    response = client.post("/api/v1/users", json=user_data.model_dump())
```

### Testing Async Endpoints

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/async-endpoint")
        assert response.status_code == 200
```
