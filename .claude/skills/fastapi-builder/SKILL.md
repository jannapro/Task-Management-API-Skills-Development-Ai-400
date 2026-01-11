---
name: fastapi-builder
description: "Build FastAPI projects from hello world to production-ready applications. Use when the user wants to: (1) Create a new FastAPI project or API, (2) Add features to existing FastAPI code (database, authentication, testing), (3) Structure or refactor a FastAPI application, (4) Learn FastAPI best practices and patterns, (5) Deploy a FastAPI application. Triggers include requests like 'build a FastAPI API', 'create FastAPI project', 'add database to FastAPI', 'implement authentication in FastAPI', or 'deploy my FastAPI app'."
---

# FastAPI Builder

Build FastAPI applications with progressive complexity from hello world to production-ready APIs.

## Quick Start

Choose your starting point based on project needs:

### 1. Hello World (Learning/Prototyping)

Use `assets/hello-world/` template for:
- Learning FastAPI basics
- Quick prototypes
- Simple APIs without database

```bash
cp -r assets/hello-world/ /path/to/myproject
cd myproject
pip install -r requirements.txt
fastapi dev main.py
```

Features: Basic endpoints, path/query parameters, auto-documentation

### 2. Intermediate API (Most Projects)

Use `assets/intermediate-api/` template for:
- Production applications with database
- CRUD operations
- Proper project structure

```bash
cp -r assets/intermediate-api/ /path/to/myproject
cd myproject
pip install -r requirements.txt
cp .env.example .env
fastapi dev main.py
```

Features: SQLAlchemy, Pydantic schemas, CRUD layer, routers, database integration

### 3. Production-Ready (Enterprise)

Use `assets/production-ready/` template for:
- Full production applications
- Apps requiring authentication
- Projects needing testing and deployment configs

```bash
cp -r assets/production-ready/ /path/to/myproject
cd myproject
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set SECRET_KEY
fastapi dev main.py
```

Features: JWT auth, role-based access, testing suite, Docker configs, logging, CORS, security

## Helper Script

Use the initialization script to create projects:

```bash
python scripts/init_project.py myapp hello-world
python scripts/init_project.py myapi intermediate-api
python scripts/init_project.py prodapp production-ready --path /custom/path
```

## Progressive Learning Path

### Level 1: Hello World → Basic API

**What you learn:**
- FastAPI application structure
- Path operations and decorators
- Path and query parameters
- Automatic documentation

**Template:** `assets/hello-world/`

**Next step:** Add database integration (Level 2)

### Level 2: Intermediate → Structured API

**What you learn:**
- Project organization (models, schemas, CRUD, routers)
- SQLAlchemy ORM integration
- Pydantic validation
- Dependency injection
- Separation of concerns

**Template:** `assets/intermediate-api/`

**Reference:** See `references/project-structure.md` and `references/database.md`

**Next step:** Add authentication and testing (Level 3)

### Level 3: Production → Enterprise API

**What you learn:**
- JWT authentication
- Role-based access control
- Testing with pytest
- Docker deployment
- Security best practices
- Environment configuration
- Logging and monitoring

**Template:** `assets/production-ready/`

**References:** See all reference docs for deep dives

## Adding Features to Existing Projects

### Add Database Integration

See `references/database.md` for:
- SQLAlchemy setup
- Model definitions
- CRUD operations
- Migrations with Alembic

Copy from `assets/intermediate-api/`:
- `app/database.py`
- `app/models/` directory
- `app/crud/` directory

### Add Authentication

See `references/authentication.md` for:
- Password hashing
- JWT tokens
- OAuth2 implementation
- Protected routes
- Role-based access

Copy from `assets/production-ready/`:
- `app/core/security.py`
- `app/services/auth.py`
- `app/routers/auth.py`

### Add Testing

See `references/testing.md` for:
- Test setup with pytest
- Database testing patterns
- Authentication testing
- Fixtures and mocking

Copy from `assets/production-ready/`:
- `tests/` directory
- `tests/conftest.py`

### Add Deployment Configs

See `references/deployment.md` for:
- Docker setup
- Cloud deployment (AWS, GCP, Azure)
- PaaS options (Heroku, Railway, Render)
- Kubernetes configs

Copy from `assets/production-ready/`:
- `Dockerfile`
- `docker-compose.yml`
- Gunicorn configs

## Common Workflows

### Creating a New CRUD API

1. Choose template based on complexity needs
2. Copy template to project directory
3. Define your model in `app/models/`
4. Create Pydantic schema in `app/schemas/`
5. Implement CRUD operations in `app/crud/`
6. Create router endpoints in `app/routers/`
7. Register router in `main.py`

See `assets/intermediate-api/` for working example with User model.

### Adding Authentication to Existing API

1. Review `references/authentication.md`
2. Copy security utilities from `assets/production-ready/app/core/security.py`
3. Add auth service from `assets/production-ready/app/services/auth.py`
4. Create auth router from `assets/production-ready/app/routers/auth.py`
5. Add password field to user model
6. Protect endpoints with `Depends(get_current_user)`

### Structuring an Unorganized Project

1. Review `references/project-structure.md` for best practices
2. Create directory structure:
   ```
   app/
   ├── core/       # Config, security
   ├── models/     # Database models
   ├── schemas/    # Pydantic models
   ├── crud/       # Database operations
   ├── services/   # Business logic
   └── routers/    # API endpoints
   ```
3. Separate concerns: move DB logic to CRUD, validation to schemas, endpoints to routers
4. Use dependency injection for database sessions

### Deploying to Production

1. Review `references/deployment.md` for platform options
2. For Docker deployment:
   - Copy `Dockerfile` and `docker-compose.yml` from production template
   - Set environment variables
   - Build and run: `docker-compose up`
3. For cloud platforms:
   - Follow platform-specific guides in deployment reference
   - Set up environment variables
   - Configure database connection
   - Deploy application

## Reference Documentation

Load these as needed for detailed information:

- **`references/project-structure.md`** - Best practices for organizing FastAPI projects, directory structure, separation of concerns
- **`references/database.md`** - SQLAlchemy integration, models, CRUD operations, migrations, async patterns
- **`references/authentication.md`** - JWT tokens, OAuth2, password hashing, protected routes, RBAC, security best practices
- **`references/testing.md`** - Pytest setup, test patterns, fixtures, mocking, coverage, CI/CD
- **`references/deployment.md`** - Docker, Kubernetes, cloud platforms (AWS/GCP/Azure), PaaS options, production checklist

## Decision Guide

**Choose hello-world if:**
- Learning FastAPI for the first time
- Building a simple prototype
- No database needed
- Quick API for personal use

**Choose intermediate-api if:**
- Building a real application
- Need database integration
- Want proper project structure
- Planning to scale the project

**Choose production-ready if:**
- Need user authentication
- Require role-based access control
- Want testing infrastructure
- Planning production deployment
- Need Docker/deployment configs

**Start simple, migrate up:**
You can always start with hello-world and add features incrementally by copying components from more complex templates.

## Best Practices

1. **Start Simple** - Use the simplest template that meets your needs
2. **Read References** - Load reference docs when implementing specific features
3. **Follow Structure** - Keep models, schemas, CRUD, and routers separate
4. **Use Dependency Injection** - Leverage FastAPI's dependency system
5. **Validate at API Layer** - Use Pydantic schemas for all input/output
6. **Test Your Code** - Add tests as you build features
7. **Secure by Default** - Hash passwords, use environment variables, implement proper CORS
8. **Document APIs** - FastAPI auto-generates docs, but add clear docstrings

## Troubleshooting

**Import errors:**
- Ensure `app/__init__.py` exists
- Use absolute imports: `from app.models.user import User`

**Database connection issues:**
- Check `DATABASE_URL` in `.env`
- Ensure database is running
- Verify connection string format

**Authentication not working:**
- Verify `SECRET_KEY` is set in `.env`
- Check token is included in Authorization header: `Bearer <token>`
- Ensure user exists and is active

**Tests failing:**
- Check test database configuration in `conftest.py`
- Ensure fixtures are properly scoped
- Verify database cleanup between tests

For detailed troubleshooting, see the specific reference documentation for the feature area.
