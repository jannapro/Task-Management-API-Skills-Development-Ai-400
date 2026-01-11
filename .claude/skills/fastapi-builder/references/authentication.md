# Authentication & Security in FastAPI

## Overview

This guide covers implementing secure authentication with JWT tokens, OAuth2, password hashing, and role-based access control.

## Password Hashing

### Setup

```bash
pip install passlib[bcrypt]
```

### Implementation

```python
# app/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### Usage

```python
# When creating a user
hashed_password = get_password_hash(user.password)
db_user = User(email=user.email, hashed_password=hashed_password)

# When authenticating
if verify_password(password, user.hashed_password):
    # Password is correct
    pass
```

## JWT Tokens

### Setup

```bash
pip install python-jose[cryptography]
pip install python-multipart
```

### Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### Create JWT Token

```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        subject: The subject of the token (usually user ID or email)
        expires_delta: Token expiration time
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt
```

### Verify JWT Token

```python
from jose import JWTError, jwt
from fastapi import HTTPException, status

def decode_access_token(token: str) -> str:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
```

## OAuth2 with Password Flow

### Token Schemas

```python
# app/schemas/token.py
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str | None = None
```

### Login Endpoint

```python
# app/routers/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.schemas.token import Token
from app.crud import user as crud_user

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login.

    Use username and password to get an access token.
    """
    # Authenticate user
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email,
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token)
```

## Protected Routes

### Get Current User

```python
# app/services/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database import get_db
from app.models.user import User
from app.crud import user as crud_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud_user.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
```

### Protected Endpoint

```python
# app/routers/users.py
from fastapi import APIRouter, Depends
from app.services.auth import get_current_active_user
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information (requires authentication)."""
    return current_user
```

## Role-Based Access Control (RBAC)

### User Model with Roles

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
```

### Permission Dependencies

```python
# app/services/auth.py

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure the current user is a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

### Admin-Only Endpoint

```python
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Admin only
):
    """Delete a user (superuser only)."""
    crud_user.delete_user(db, user_id)
    return {"message": "User deleted"}
```

## Advanced: Permission-Based Access

### Custom Permissions

```python
from enum import Enum

class Permission(str, Enum):
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"

# app/models/user.py
from sqlalchemy import Column, ARRAY, String

class User(Base):
    __tablename__ = "users"
    # ... other fields
    permissions = Column(ARRAY(String))  # PostgreSQL only
```

### Permission Checker

```python
# app/services/auth.py
from app.models.user import Permission

def has_permission(required_permission: Permission):
    """Dependency to check if user has specific permission."""
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ):
        if required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        return current_user
    return permission_checker
```

### Usage

```python
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(has_permission(Permission.DELETE_USERS))
):
    """Delete a user (requires delete:users permission)."""
    # ...
```

## Refresh Tokens (Advanced)

### Implementation

```python
# Create both access and refresh tokens
def create_tokens(user_id: str):
    access_token_expires = timedelta(minutes=15)
    refresh_token_expires = timedelta(days=7)

    access_token = create_access_token(
        subject=user_id,
        expires_delta=access_token_expires
    )

    refresh_token = create_access_token(
        subject=user_id,
        expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# Refresh endpoint
@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Get a new access token using a refresh token."""
    # Verify refresh token
    user_id = decode_access_token(refresh_token)

    # Create new access token
    access_token = create_access_token(subject=user_id)

    return Token(access_token=access_token)
```

## Security Best Practices

### 1. Environment Variables

```python
# .env
SECRET_KEY=generate-a-strong-random-key-here
DATABASE_URL=postgresql://user:password@localhost/db

# Never commit .env to git!
```

Generate secure secret key:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 2. HTTPS Only in Production

```python
# main.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 3. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourfrontend.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Specific methods
    allow_headers=["*"],
)
```

### 4. Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # Max 5 requests per minute
async def login(...):
    pass
```

### 5. Password Requirements

```python
from pydantic import BaseModel, field_validator
import re

class UserCreate(BaseModel):
    email: str
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain number')
        return v
```

### 6. SQL Injection Prevention

SQLAlchemy ORM prevents SQL injection by default. Always use ORM queries:

```python
# ✅ Safe (parameterized)
db.query(User).filter(User.email == email).first()

# ❌ Unsafe (never do this)
db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

## Common Security Pitfalls

❌ **Weak secret keys** - Use strong random keys
❌ **Storing plain passwords** - Always hash passwords
❌ **No token expiration** - Set reasonable expiration times
❌ **Exposing sensitive data** - Never return hashed_password in responses
❌ **No rate limiting** - Prevent brute force attacks
❌ **Weak CORS** - Don't use allow_origins=["*"] in production
❌ **HTTP in production** - Always use HTTPS
❌ **Hardcoded secrets** - Use environment variables
