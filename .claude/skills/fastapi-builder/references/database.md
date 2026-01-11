# Database Integration with SQLAlchemy

## Overview

FastAPI works seamlessly with SQLAlchemy, the most popular Python ORM. This guide covers database setup, models, and best practices.

## Database Setup

### Installation

```bash
pip install sqlalchemy
# For async: pip install sqlalchemy[asyncio]

# Database drivers:
pip install psycopg2-binary  # PostgreSQL
pip install pymysql           # MySQL
# SQLite is included with Python
```

### Basic Configuration

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"
# PostgreSQL: "postgresql://user:password@localhost/dbname"
# MySQL: "mysql+pymysql://user:password@localhost/dbname"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Create Tables

```python
# main.py
from app.database import Base, engine
from app.models import user  # Import models

# Create all tables
Base.metadata.create_all(bind=engine)
```

## Defining Models

### Basic Model

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
```

### Column Types

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON
from datetime import datetime

class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))           # VARCHAR(255)
    description = Column(Text)            # Unlimited text
    price = Column(Float)                 # Float number
    is_active = Column(Boolean, default=True)
    metadata_json = Column(JSON)          # JSON field
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Relationships

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)

    # One-to-many: User has many items
    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Many-to-one: Item belongs to one user
    owner = relationship("User", back_populates="items")
```

### Many-to-Many Relationships

```python
from sqlalchemy import Table, Column, Integer, ForeignKey

# Association table
user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    groups = relationship("Group", secondary=user_groups, back_populates="users")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    users = relationship("User", secondary=user_groups, back_populates="groups")
```

## CRUD Operations

### Basic Operations

```python
# app/crud/user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def get_user(db: Session, user_id: int):
    """Get a single user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get multiple users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    """Create a new user."""
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Get updated data from DB
    return db_user

def update_user(db: Session, user_id: int, user_update: dict):
    """Update a user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    for key, value in user_update.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Delete a user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
```

### Advanced Queries

```python
from sqlalchemy import and_, or_, func

# Multiple filters
users = db.query(User).filter(
    and_(User.is_active == True, User.email.like("%@example.com"))
).all()

# OR conditions
users = db.query(User).filter(
    or_(User.username == "admin", User.is_superuser == True)
).all()

# Count
user_count = db.query(func.count(User.id)).scalar()

# Order by
users = db.query(User).order_by(User.created_at.desc()).all()

# Join
from app.models.item import Item

results = db.query(User, Item).join(Item).filter(User.id == Item.owner_id).all()

# Exists
from sqlalchemy import exists

has_admin = db.query(exists().where(User.username == "admin")).scalar()
```

## Pydantic Integration

### Separate Schemas from Models

```python
# app/schemas/user.py
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    """Shared properties."""
    email: str
    username: str

class UserCreate(UserBase):
    """Properties for creation."""
    password: str

class User(UserBase):
    """Properties in DB and returned to client."""
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode
```

### Using in Routes

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import User, UserCreate
from app.crud import user as crud_user

@app.post("/users", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user)

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return crud_user.get_user(db, user_id)
```

## Database Migrations with Alembic

### Setup

```bash
pip install alembic
alembic init alembic
```

### Configure

```python
# alembic/env.py
from app.database import Base
from app.models import user, item  # Import all models

target_metadata = Base.metadata
```

### Create Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add users table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Connection Pooling (Production)

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,          # Number of connections
    max_overflow=10,      # Extra connections when pool full
    pool_timeout=30,      # Seconds to wait for connection
    pool_recycle=3600,    # Recycle connections after 1 hour
)
```

## Async SQLAlchemy (Optional)

### Setup

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/db"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session
```

### Async CRUD

```python
from sqlalchemy import select

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()
```

## Best Practices

1. **Use dependency injection** - `Depends(get_db)` in routes
2. **Close sessions** - Always use try/finally or context managers
3. **Separate schemas from models** - Models for DB, Pydantic for API
4. **Use migrations** - Never modify models directly in production
5. **Index frequently queried fields** - `index=True` on columns
6. **Use connection pooling** - For production databases
7. **Validate at API layer** - Use Pydantic schemas
8. **Handle NULL properly** - Use `nullable=False` when appropriate
9. **Use transactions** - Wrap related operations in a transaction
10. **Lazy load carefully** - Be aware of N+1 query problems

## Common Patterns

### Soft Delete

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    deleted_at = Column(DateTime, nullable=True)

def get_active_users(db: Session):
    return db.query(User).filter(User.deleted_at.is_(None)).all()
```

### Timestamps

```python
from datetime import datetime

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
```

### UUID Primary Keys

```python
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```
