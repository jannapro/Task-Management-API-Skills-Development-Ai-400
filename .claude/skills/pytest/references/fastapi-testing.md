# FastAPI Testing Patterns

Comprehensive guide for testing FastAPI applications with pytest.

## Table of Contents

1. [Test Client Setup](#test-client-setup)
2. [Dependency Overrides](#dependency-overrides)
3. [Database Testing](#database-testing)
4. [Authentication Testing](#authentication-testing)
5. [Async Testing](#async-testing)
6. [Testing File Uploads](#testing-file-uploads)
7. [Testing WebSockets](#testing-websockets)

## Test Client Setup

### Basic TestClient

```python
from fastapi.testclient import TestClient
from myapp.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

### TestClient Fixture

```python
import pytest
from fastapi.testclient import TestClient
from myapp.main import app

@pytest.fixture
def client():
    """Reusable test client."""
    return TestClient(app)

def test_endpoint(client):
    response = client.get("/items/1")
    assert response.status_code == 200
```

### Async Client for Async Endpoints

```python
import pytest
from httpx import AsyncClient
from myapp.main import app

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/async-items")
    assert response.status_code == 200
```

## Dependency Overrides

### Override Database Dependency

```python
from fastapi import Depends
from sqlalchemy.orm import Session

# Original dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
```

### Override Auth Dependency

```python
from myapp.auth import get_current_user

# Override to bypass auth in tests
def override_get_current_user():
    return {"user_id": 1, "username": "testuser"}

app.dependency_overrides[get_current_user] = override_get_current_user
```

### Fixture-Based Override

```python
@pytest.fixture
def mock_user():
    """Override auth dependency for testing."""
    def _override():
        return {"user_id": 123, "username": "test"}

    app.dependency_overrides[get_current_user] = _override
    yield
    app.dependency_overrides.clear()

def test_protected_route(client, mock_user):
    response = client.get("/protected")
    assert response.status_code == 200
```

## Database Testing

### In-Memory SQLite Test Database

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from myapp.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Transaction Rollback Pattern

```python
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### Test Data Factories

```python
import pytest
from myapp.models import User

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_here"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_get_user(client, test_user):
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

## Authentication Testing

### JWT Token Testing

```python
from myapp.auth import create_access_token

@pytest.fixture
def auth_headers():
    """Generate auth headers with JWT token."""
    token = create_access_token(data={"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}

def test_protected_endpoint(client, auth_headers):
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
```

### Testing Login Flow

```python
def test_login_success(client):
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == 401
```

### Parametrized Auth Tests

```python
@pytest.mark.parametrize("username,password,expected_status", [
    ("valid@email.com", "ValidPass123", 200),
    ("invalid@email.com", "wrong", 401),
    ("", "", 422),
    ("no@password.com", "", 422),
])
def test_login_scenarios(client, username, password, expected_status):
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password}
    )
    assert response.status_code == expected_status
```

## Async Testing

### Async Test Setup

```python
import pytest

# Configure pytest to handle async tests
pytest_plugins = ('pytest_asyncio',)

@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### Testing Async Endpoints

```python
@pytest.mark.asyncio
async def test_create_item():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/items/",
            json={"name": "Test Item", "price": 10.99}
        )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"
```

### Testing Background Tasks

```python
import asyncio

@pytest.mark.asyncio
async def test_background_task():
    # Trigger endpoint with background task
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/process-data")

    assert response.status_code == 202

    # Wait for background task to complete
    await asyncio.sleep(0.5)

    # Verify background task results
    async with AsyncClient(app=app, base_url="http://test") as ac:
        check_response = await ac.get("/task-status")
    assert check_response.json()["status"] == "completed"
```

## Testing File Uploads

### Single File Upload

```python
from io import BytesIO

def test_upload_file(client):
    file_content = b"test file content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

    response = client.post("/upload", files=files)
    assert response.status_code == 200
    assert "filename" in response.json()
```

### Multiple File Upload

```python
def test_upload_multiple_files(client):
    files = [
        ("files", ("file1.txt", BytesIO(b"content1"), "text/plain")),
        ("files", ("file2.txt", BytesIO(b"content2"), "text/plain")),
    ]

    response = client.post("/upload-multiple", files=files)
    assert response.status_code == 200
    assert len(response.json()["files"]) == 2
```

### File Upload with Form Data

```python
def test_upload_with_metadata(client):
    files = {"file": ("test.txt", BytesIO(b"content"), "text/plain")}
    data = {"description": "Test file", "category": "documents"}

    response = client.post("/upload-with-data", files=files, data=data)
    assert response.status_code == 200
```

## Testing WebSockets

### WebSocket Connection Test

```python
def test_websocket():
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connection_established"
```

### WebSocket Message Exchange

```python
def test_websocket_messages():
    with client.websocket_connect("/ws/chat") as websocket:
        # Send message
        websocket.send_json({"message": "Hello"})

        # Receive response
        response = websocket.receive_json()
        assert response["message"] == "Hello"
```

### WebSocket Authentication

```python
def test_websocket_with_auth():
    token = create_access_token(data={"sub": "testuser"})

    with client.websocket_connect(f"/ws?token={token}") as websocket:
        data = websocket.receive_json()
        assert data["user"] == "testuser"
```

## Common Testing Patterns

### Setup and Teardown

```python
@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset app state before each test."""
    # Setup
    app.dependency_overrides.clear()

    yield

    # Teardown
    app.dependency_overrides.clear()
```

### Testing Validation Errors

```python
@pytest.mark.parametrize("invalid_data,expected_field", [
    ({"name": ""}, "name"),
    ({"price": -1}, "price"),
    ({"quantity": "not a number"}, "quantity"),
])
def test_validation_errors(client, invalid_data, expected_field):
    response = client.post("/items", json=invalid_data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(err["loc"][-1] == expected_field for err in errors)
```

### Testing Error Responses

```python
def test_not_found(client):
    response = client.get("/items/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_server_error_handling(client, monkeypatch):
    def mock_error(*args, **kwargs):
        raise Exception("Database connection failed")

    monkeypatch.setattr("myapp.database.query", mock_error)

    response = client.get("/items")
    assert response.status_code == 500
```

### Testing Pagination

```python
def test_pagination(client):
    # Test first page
    response = client.get("/items?page=1&size=10")
    assert response.status_code == 200
    assert len(response.json()["items"]) <= 10
    assert "total" in response.json()
    assert "page" in response.json()
```
