# Deploying FastAPI Applications

## Overview

This guide covers various deployment strategies for FastAPI applications, from simple platforms to containerized production deployments.

## Local Production Server

### Uvicorn (Development/Small Production)

```bash
# Basic production run
uvicorn main:app --host 0.0.0.0 --port 8000

# With auto-reload (development only)
uvicorn main:app --reload

# With workers (production)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With specific settings
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info \
  --access-log
```

### Gunicorn with Uvicorn Workers (Production)

```bash
# Install gunicorn
pip install gunicorn

# Run with uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### Gunicorn Configuration

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
errorlog = "-"
accesslog = "-"
loglevel = "info"
```

Run with config:
```bash
gunicorn main:app -c gunicorn.conf.py
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Multi-stage Build (Optimized)

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/app
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
```

### Build and Run

```bash
# Build image
docker build -t myapp .

# Run container
docker run -d -p 8000:8000 --env-file .env myapp

# With docker-compose
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop
docker-compose down
```

## Nginx Reverse Proxy

### Basic Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream fastapi {
        server web:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        location / {
            proxy_pass http://fastapi;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### HTTPS with SSL

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Platform-as-a-Service (PaaS) Deployments

### Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create myapp

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ENVIRONMENT=production

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

#### Procfile

```
web: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

#### runtime.txt

```
python-3.11.0
```

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Set environment variables
railway variables set SECRET_KEY=your-secret-key
```

### Render

Create `render.yaml`:

```yaml
services:
  - type: web
    name: fastapi-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: mydb
          property: connectionString

databases:
  - name: mydb
    databaseName: app
    user: app
```

## Cloud Platforms

### AWS (Elastic Beanstalk)

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 myapp

# Create environment
eb create production

# Deploy
eb deploy

# Open app
eb open
```

#### .ebextensions/python.config

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: main:app
```

### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy myapp \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Dockerfile for Cloud Run

```dockerfile
FROM python:3.11-slim

ENV PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind :$PORT
```

### Azure App Service

```bash
# Login
az login

# Create resource group
az group create --name myResourceGroup --location eastus

# Create App Service plan
az appservice plan create --name myPlan --resource-group myResourceGroup --sku B1 --is-linux

# Create web app
az webapp create --resource-group myResourceGroup --plan myPlan --name myapp --runtime "PYTHON:3.11"

# Deploy
az webapp up --name myapp --resource-group myResourceGroup
```

## Kubernetes Deployment

### Deployment YAML

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: myregistry/fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: secret-key
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service YAML

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Apply

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## Production Checklist

### Environment Configuration

- [ ] Set strong `SECRET_KEY`
- [ ] Use production database (PostgreSQL/MySQL, not SQLite)
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `ALLOWED_ORIGINS` for CORS
- [ ] Set proper logging levels
- [ ] Use environment variables for all secrets

### Security

- [ ] Enable HTTPS/SSL
- [ ] Set up proper CORS
- [ ] Implement rate limiting
- [ ] Use secure headers middleware
- [ ] Validate all inputs
- [ ] Hash passwords properly
- [ ] Set token expiration times
- [ ] Keep dependencies updated

### Performance

- [ ] Use connection pooling for database
- [ ] Set appropriate number of workers
- [ ] Enable gzip compression
- [ ] Use caching (Redis) where appropriate
- [ ] Optimize database queries
- [ ] Set up CDN for static files

### Monitoring & Logging

- [ ] Set up application logging
- [ ] Configure error tracking (Sentry)
- [ ] Monitor performance (New Relic, DataDog)
- [ ] Set up health checks
- [ ] Configure alerts
- [ ] Enable access logs

### Database

- [ ] Run migrations properly
- [ ] Set up database backups
- [ ] Use read replicas if needed
- [ ] Monitor database performance
- [ ] Set up connection limits

### Reliability

- [ ] Configure auto-restart on failure
- [ ] Set up horizontal scaling
- [ ] Implement graceful shutdown
- [ ] Use load balancer
- [ ] Set up database failover
- [ ] Regular backups

## Environment-Specific Settings

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    class Config:
        env_file = ".env"

settings = Settings()

# Use in main.py
if settings.is_production:
    # Production-only middleware
    app.add_middleware(HTTPSRedirectMiddleware)
else:
    # Development-only features
    app.debug = True
```

## Health Checks

```python
# main.py
from sqlalchemy import text

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for load balancers."""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )
```

## Graceful Shutdown

```python
# main.py
import signal
import sys

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    print("Shutting down gracefully...")
    # Close database connections
    # Finish pending requests
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
```

## Common Deployment Issues

### Issue: Workers Running Out of Memory

**Solution:** Reduce number of workers or increase memory allocation

```bash
# Reduce workers
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker

# Or increase memory in Docker
docker run -m 1g myapp
```

### Issue: Database Connection Pool Exhausted

**Solution:** Configure pool size properly

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10
)
```

### Issue: Slow Startup Time

**Solution:** Use preload for gunicorn

```bash
gunicorn main:app --preload --workers 4
```

### Issue: CORS Errors in Production

**Solution:** Configure CORS properly

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
