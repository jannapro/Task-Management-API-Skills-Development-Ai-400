from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Intermediate FastAPI Project",
    description="A FastAPI application with database integration and proper structure",
    version="1.0.0"
)

# Include routers
app.include_router(users.router, prefix="/api/v1", tags=["users"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the API", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
