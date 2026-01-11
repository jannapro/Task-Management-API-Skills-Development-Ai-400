# FastAPI Project Structure Best Practices

## Overview

A well-organized FastAPI project follows a modular structure that separates concerns and scales with your application.

## Recommended Structure

### Basic Structure (Hello World → Small Projects)

```
project/
├── main.py              # Application entry point
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
├── .gitignore
└── README.md
```

### Intermediate Structure (Medium Projects)

```
project/
├── main.py
├── app/
│   ├── __init__.py
│   ├── database.py      # Database configuration
│   ├── models/          # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/         # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user.py
│   ├── crud/            # Database operations
│   │   ├── __init__.py
│   │   └── user.py
│   └── routers/         # API endpoints
│       ├── __init__.py
│       └── users.py
├── requirements.txt
├── .env
└── README.md
```

### Production Structure (Large Projects)

```
project/
├── main.py
├── app/
│   ├── __init__.py
│   ├── core/            # Core functionality
│   │   ├── config.py    # Settings
│   │   ├── security.py  # Auth utilities
│   │   └── deps.py      # Dependencies
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py      # Base CRUD class
│   │   ├── user.py
│   │   └── item.py
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   └── auth.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       └── users.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_users.py
├── alembic/             # Database migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Directory Purposes

### `app/core/`
Core application configuration and utilities:
- `config.py` - Environment-based settings with Pydantic
- `security.py` - Authentication, password hashing, JWT
- `deps.py` - Reusable dependencies (DB sessions, auth)

### `app/models/`
SQLAlchemy ORM models (database tables):
- Define database schema
- One model per file for larger projects
- Use `__init__.py` to export models

### `app/schemas/`
Pydantic models for validation:
- Request schemas (what comes in)
- Response schemas (what goes out)
- Separate from database models for flexibility

### `app/crud/`
Database operations (Create, Read, Update, Delete):
- Pure database logic
- No business rules
- Reusable functions

### `app/services/`
Business logic layer:
- Complex operations involving multiple CRUD functions
- External API calls
- Email sending, file processing, etc.

### `app/routers/`
API route handlers:
- Define endpoints
- Handle HTTP requests/responses
- Validate input, call services/CRUD
- Return formatted responses

## File Naming Conventions

- **Snake_case** for Python files: `user_service.py`
- **PascalCase** for classes: `class UserService`
- **Lowercase** for directories: `routers/`, `models/`
- **Descriptive names**: `user.py` not `u.py`

## Best Practices

### 1. Separation of Concerns

**Bad:**
```python
# All in one file
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404)
    return user
```

**Good:**
```python
# Router (routers/users.py)
@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(404)
    return user

# CRUD (crud/user.py)
def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()
```

### 2. Use Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### 3. Environment-Based Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 4. Modular Routers

```python
# main.py
from app.routers import users, items

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])
```

### 5. Consistent Import Style

```python
# Absolute imports
from app.models.user import User
from app.schemas.user import UserCreate
from app.crud import user as crud_user

# Not relative imports in production
# from ..models.user import User
```

## When to Refactor

### Start Simple → Refactor as Needed

1. **Start**: Single `main.py` file for prototypes
2. **Add routers**: When you have 3+ endpoint groups
3. **Add models/schemas**: When using a database
4. **Add crud/**: When DB logic gets complex
5. **Add services/**: When business logic spans multiple CRUD operations
6. **Add core/**: When you need centralized config/security

## Common Mistakes to Avoid

❌ **Circular imports** - Use `from typing import TYPE_CHECKING` for type hints
❌ **Mixing concerns** - Business logic in routers
❌ **No separation** - Models and schemas should be separate
❌ **Hardcoded values** - Use environment variables
❌ **Deep nesting** - Keep imports and structure flat
