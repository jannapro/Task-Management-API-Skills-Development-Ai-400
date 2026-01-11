# Production-Ready FastAPI Application

A complete FastAPI application with authentication, testing, and deployment ready for production use.

## Features

- ✅ **JWT Authentication** - Secure user authentication with OAuth2
- ✅ **Database Integration** - SQLAlchemy ORM with migrations support
- ✅ **Proper Project Structure** - Organized code following best practices
- ✅ **Data Validation** - Pydantic schemas for request/response validation
- ✅ **Authorization** - Role-based access control (superuser)
- ✅ **Testing** - Comprehensive test suite with pytest
- ✅ **Docker Support** - Containerized deployment
- ✅ **CORS Middleware** - Configured for cross-origin requests
- ✅ **Environment Configuration** - Settings management with Pydantic
- ✅ **Logging** - Structured logging for monitoring
- ✅ **API Documentation** - Auto-generated Swagger UI and ReDoc

## Project Structure

```
.
├── main.py                 # Application entry point
├── app/
│   ├── core/               # Core functionality
│   │   ├── config.py       # Settings and configuration
│   │   └── security.py     # Security utilities (JWT, password hashing)
│   ├── database.py         # Database configuration
│   ├── models/             # SQLAlchemy models
│   │   └── user.py
│   ├── schemas/            # Pydantic schemas
│   │   ├── user.py
│   │   └── token.py
│   ├── crud/               # CRUD operations
│   │   └── user.py
│   ├── services/           # Business logic
│   │   └── auth.py         # Authentication service
│   └── routers/            # API route handlers
│       ├── auth.py         # Auth endpoints
│       └── users.py        # User endpoints
├── tests/                  # Test suite
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_users.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

## Setup

### Local Development

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
# Edit .env and set your SECRET_KEY and other settings
```

4. Run the application:
```bash
fastapi dev main.py
```

The API will be available at `http://127.0.0.1:8000`

### Docker Development

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

This starts both the FastAPI app and a PostgreSQL database.

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token

### Users

- `GET /api/v1/users/me` - Get current user (authenticated)
- `PUT /api/v1/users/me` - Update current user (authenticated)
- `GET /api/v1/users/` - List all users (superuser only)
- `GET /api/v1/users/{user_id}` - Get specific user
- `DELETE /api/v1/users/{user_id}` - Delete user (superuser only)

## Documentation

- Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`
- Alternative docs (ReDoc): `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/api/v1/openapi.json`

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

## Authentication Flow

1. **Register**: `POST /api/v1/auth/register` with email, username, and password
2. **Login**: `POST /api/v1/auth/login` with credentials to get JWT token
3. **Authenticated Requests**: Include token in Authorization header:
   ```
   Authorization: Bearer <your-token>
   ```

## Environment Variables

See `.env.example` for all available configuration options:

- `PROJECT_NAME` - Application name
- `ENVIRONMENT` - Environment (development/production)
- `SECRET_KEY` - JWT secret key (change in production!)
- `DATABASE_URL` - Database connection string
- `ALLOWED_ORIGINS` - CORS allowed origins

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- OAuth2 with Password flow
- Role-based access control (superuser)
- CORS middleware configuration
- Secure password requirements

## Deployment

### Production Considerations

1. **Change SECRET_KEY**: Generate a secure random key
2. **Use PostgreSQL**: Change DATABASE_URL from SQLite
3. **Set ENVIRONMENT=production**: Disables debug features
4. **Configure CORS**: Update ALLOWED_ORIGINS
5. **Use HTTPS**: Deploy behind reverse proxy (nginx)
6. **Enable logging**: Configure structured logging
7. **Database migrations**: Use Alembic for schema changes
8. **Rate limiting**: Add rate limiting middleware
9. **Input validation**: Already handled by Pydantic
10. **Secrets management**: Use environment-specific configs

### Docker Production Deployment

```bash
docker build -t myapp .
docker run -p 8000:8000 --env-file .env myapp
```

## Next Steps

- [ ] Add database migrations with Alembic
- [ ] Implement password reset functionality
- [ ] Add email verification
- [ ] Implement refresh tokens
- [ ] Add rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure CI/CD pipeline
- [ ] Add more comprehensive logging
- [ ] Implement caching with Redis
- [ ] Add WebSocket support for real-time features
