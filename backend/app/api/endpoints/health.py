"""
Health Check Endpoints
System health and status monitoring
"""

from fastapi import APIRouter, Depends
from app.core.config import Settings, get_settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/")
async def health_check(settings: Settings = Depends(get_settings)):
    """Basic health check"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check(settings: Settings = Depends(get_settings)):
    """Detailed health check with service status"""
    
    health_status = {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "azure_speech": "unknown",
            "claude_api": "unknown",
            "redis": "unknown"
        }
    }
    
    # TODO: Add actual service health checks
    # - Test Azure Speech SDK connection
    # - Test Claude API connection
    # - Test Redis connection
    
    logger.info("Health check performed", **health_status)
    
    return health_status
