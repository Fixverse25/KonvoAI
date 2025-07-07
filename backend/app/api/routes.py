"""
EVA-Dev API Routes
Main router that includes all API endpoints
"""

from fastapi import APIRouter

from app.api.endpoints import chat, voice, health

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
