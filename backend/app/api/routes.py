"""
EVA-Dev API Routes
Main router that includes all API endpoints
"""

from fastapi import APIRouter

from app.api.endpoints import chat, voice, health, gdpr

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

api_router.include_router(
    voice.router,
    prefix="/voice",
    tags=["voice"]
)

api_router.include_router(
    gdpr.router,
    prefix="/gdpr",
    tags=["gdpr", "privacy"]
)
