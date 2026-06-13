"""
Router aggregation — combines all API route modules.
"""

from fastapi import APIRouter

from app.api.routes import assets, auth, digital_twins, generation, health, projects, providers

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(assets.router)
api_router.include_router(generation.router)
api_router.include_router(digital_twins.router)
api_router.include_router(providers.router)
