"""
Shared pytest fixtures and configuration.

This conftest.py file is automatically discovered by pytest and makes
fixtures available to all test files in this directory and subdirectories.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your app components
# from myapp.main import app
# from myapp.database import Base, get_db
# from myapp.models import User


# ============================================================================
# Test Database Configuration
# ============================================================================

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def db_engine():
    """Create a fresh database for each test."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    # Base.metadata.create_all(bind=engine)
    yield engine
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Provide a database session for testing."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ============================================================================
# FastAPI Test Client
# ============================================================================

@pytest.fixture
def client(db_session):
    """
    FastAPI test client with overridden database dependency.

    Usage:
        def test_endpoint(client):
            response = client.get("/items")
            assert response.status_code == 200
    """
    # Override database dependency
    # def override_get_db():
    #     try:
    #         yield db_session
    #     finally:
    #         pass
    #
    # app.dependency_overrides[get_db] = override_get_db
    #
    # yield TestClient(app)
    #
    # # Clean up
    # app.dependency_overrides.clear()
    pass


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture
def test_user(db_session):
    """
    Create a test user in the database.

    Usage:
        def test_user_endpoint(client, test_user):
            response = client.get(f"/users/{test_user.id}")
            assert response.status_code == 200
    """
    # user = User(
    #     email="test@example.com",
    #     username="testuser",
    #     hashed_password="hashed_password_here"
    # )
    # db_session.add(user)
    # db_session.commit()
    # db_session.refresh(user)
    # return user
    pass


@pytest.fixture
def auth_headers(test_user):
    """
    Generate authentication headers with JWT token.

    Usage:
        def test_protected_endpoint(client, auth_headers):
            response = client.get("/protected", headers=auth_headers)
            assert response.status_code == 200
    """
    # from myapp.auth import create_access_token
    # token = create_access_token(data={"sub": test_user.username})
    # return {"Authorization": f"Bearer {token}"}
    pass


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_app_state():
    """Automatically reset application state before each test."""
    # Setup
    # app.dependency_overrides.clear()

    yield

    # Teardown
    # app.dependency_overrides.clear()
    pass


# ============================================================================
# Test Data Factories
# ============================================================================

@pytest.fixture
def sample_item_data():
    """Sample data for creating items."""
    return {
        "name": "Test Item",
        "description": "A test item",
        "price": 10.99,
        "quantity": 5
    }


@pytest.fixture
def sample_user_data():
    """Sample data for creating users."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123"
    }


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_external_api(monkeypatch):
    """
    Mock external API calls.

    Usage:
        def test_with_mocked_api(client, mock_external_api):
            response = client.get("/data-from-external-api")
            assert response.status_code == 200
    """
    def mock_fetch(*args, **kwargs):
        return {"data": "mocked response"}

    # monkeypatch.setattr("myapp.services.external_api.fetch_data", mock_fetch)
    pass
