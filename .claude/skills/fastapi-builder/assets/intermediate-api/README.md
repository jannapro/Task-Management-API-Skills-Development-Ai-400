# Intermediate FastAPI Project

A structured FastAPI application with database integration, proper project organization, and CRUD operations.

## Project Structure

```
.
├── main.py                 # Application entry point
├── app/
│   ├── __init__.py
│   ├── database.py         # Database configuration
│   ├── models/             # SQLAlchemy models
│   │   └── user.py
│   ├── schemas/            # Pydantic schemas
│   │   └── user.py
│   ├── crud/               # CRUD operations
│   │   └── user.py
│   └── routers/            # API route handlers
│       └── users.py
├── requirements.txt
└── .env
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database settings
```

4. Run the application:
```bash
fastapi dev main.py
```

The API will be available at `http://127.0.0.1:8000`

## API Endpoints

### Users

- `POST /api/v1/users` - Create a new user
- `GET /api/v1/users` - List all users (with pagination)
- `GET /api/v1/users/{user_id}` - Get a specific user
- `PUT /api/v1/users/{user_id}` - Update a user
- `DELETE /api/v1/users/{user_id}` - Delete a user

## Documentation

- Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`
- Alternative docs (ReDoc): `http://127.0.0.1:8000/redoc`

## Key Concepts Demonstrated

- **Project Structure**: Organized with separate directories for models, schemas, CRUD, and routers
- **Database Integration**: SQLAlchemy ORM with dependency injection
- **Data Validation**: Pydantic schemas for request/response validation
- **CRUD Operations**: Separation of database operations from route handlers
- **Error Handling**: Proper HTTP status codes and error messages
- **API Versioning**: Endpoints under `/api/v1` prefix

## Next Steps

- Add authentication and authorization
- Implement pagination helpers
- Add input validation and custom validators
- Set up automated testing
- Configure logging
- Add database migrations with Alembic
- Implement caching
- Add API rate limiting
