"""
Pro3duct FastAPI Application — Main entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.database import init_db

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚀 Starting Pro3duct API server...")

    # Initialize database (create tables for dev)
    if settings.environment == "development":
        await init_db()
        logger.info("✅ Database tables created")

    yield

    logger.info("👋 Shutting down Pro3duct API server...")


app = FastAPI(
    title="Pro3duct API",
    description="Interactive Digital Twin SaaS Platform — Control Plane API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "name": "Pro3duct API",
        "version": "0.1.0",
        "docs": "/api/docs",
    }
