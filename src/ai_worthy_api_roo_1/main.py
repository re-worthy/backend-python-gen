"""Main application module for the FastAPI application."""

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ai_worthy_api_roo_1.api import auth, transactions, users
from ai_worthy_api_roo_1.core.config import settings
from ai_worthy_api_roo_1.database.database import engine
from ai_worthy_api_roo_1.database.models import Base

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Create database tables on startup
@app.on_event("startup")
async def startup():
    """Create database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to the Financial Tracking API"}


# Healthcheck endpoint
@app.get("/health")
def healthcheck():
    """Healthcheck endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "ai_worthy_api_roo_1.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )