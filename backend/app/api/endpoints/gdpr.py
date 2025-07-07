"""
GDPR Compliance API Endpoints
Handles data protection requests and privacy compliance
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.gdpr_service import gdpr_service

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()

# Rate limiter for GDPR endpoints
limiter = Limiter(key_func=get_remote_address)


class ConsentRequest(BaseModel):
    """Consent request model"""
    session_id: str
    consent_given: bool
    consent_categories: list[str] = ["conversation_data", "session_metadata"]


class DataDeletionRequest(BaseModel):
    """Data deletion request model"""
    session_id: str
    confirmation: bool = False


class DataExportRequest(BaseModel):
    """Data export request model"""
    session_id: str


@router.post("/consent")
@limiter.limit("10/minute")
async def record_consent(
    request: Request,
    consent_request: ConsentRequest
) -> Dict[str, Any]:
    """
    Record user consent (GDPR Article 7)
    """
    try:
        # Validate data residency
        if not gdpr_service.validate_data_residency(str(request.client.host)):
            raise HTTPException(
                status_code=403, 
                detail="Data processing not allowed from this region"
            )
        
        # Record consent
        success = gdpr_service.record_consent(
            consent_request.session_id,
            consent_request.consent_given
        )
        
        if not success:
            # Create new data subject if doesn't exist
            gdpr_service.create_data_subject(
                consent_request.session_id,
                consent_request.consent_given
            )
        
        logger.info(f"Consent recorded for session: {consent_request.session_id}")
        
        return {
            "status": "success",
            "consent_recorded": True,
            "timestamp": gdpr_service.get_privacy_notice()["last_updated"]
        }
        
    except Exception as e:
        logger.error(f"Consent recording error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record consent")


@router.get("/consent/{session_id}")
@limiter.limit("20/minute")
async def check_consent(
    request: Request,
    session_id: str
) -> Dict[str, Any]:
    """
    Check consent status for a session
    """
    try:
        has_consent = gdpr_service.check_consent(session_id)
        
        return {
            "session_id": session_id,
            "consent_given": has_consent,
            "privacy_notice": gdpr_service.get_privacy_notice()
        }
        
    except Exception as e:
        logger.error(f"Consent check error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check consent")


@router.delete("/data/{session_id}")
@limiter.limit("5/minute")
async def delete_user_data(
    request: Request,
    session_id: str,
    deletion_request: DataDeletionRequest
) -> Dict[str, Any]:
    """
    Process right to erasure request (GDPR Article 17)
    """
    try:
        if not deletion_request.confirmation:
            raise HTTPException(
                status_code=400,
                detail="Deletion confirmation required"
            )
        
        if deletion_request.session_id != session_id:
            raise HTTPException(
                status_code=400,
                detail="Session ID mismatch"
            )
        
        # Process deletion
        deletion_result = gdpr_service.process_data_deletion(session_id)
        
        logger.info(f"Data deletion completed for session: {session_id}")
        
        return {
            "status": "completed",
            "message": "All personal data has been deleted",
            "deletion_details": deletion_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data deletion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete data")


@router.get("/export/{session_id}")
@limiter.limit("3/minute")
async def export_user_data(
    request: Request,
    session_id: str
) -> Dict[str, Any]:
    """
    Export user data for portability (GDPR Article 20)
    """
    try:
        # Check consent first
        if not gdpr_service.check_consent(session_id):
            raise HTTPException(
                status_code=403,
                detail="No valid consent found for data export"
            )
        
        # Export data
        export_data = gdpr_service.export_user_data(session_id)
        
        logger.info(f"Data export completed for session: {session_id}")
        
        return {
            "status": "success",
            "export_data": export_data,
            "format": "JSON",
            "gdpr_compliance": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data export error: {e}")
        raise HTTPException(status_code=500, detail="Failed to export data")


@router.get("/privacy-notice")
@limiter.limit("30/minute")
async def get_privacy_notice(request: Request) -> Dict[str, Any]:
    """
    Get privacy notice and GDPR information
    """
    try:
        privacy_notice = gdpr_service.get_privacy_notice()
        
        return {
            "privacy_notice": privacy_notice,
            "gdpr_compliance": True,
            "data_residency": "EU (Sweden)",
            "contact_dpo": "privacy@fixverse.se"
        }
        
    except Exception as e:
        logger.error(f"Privacy notice error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get privacy notice")


@router.get("/data-categories")
@limiter.limit("20/minute")
async def get_data_categories(request: Request) -> Dict[str, Any]:
    """
    Get information about data categories processed
    """
    try:
        return {
            "data_categories": [
                {
                    "category": "conversation_data",
                    "description": "Chat messages and AI responses",
                    "retention_days": settings.CONVERSATION_RETENTION_DAYS,
                    "legal_basis": "Legitimate interest"
                },
                {
                    "category": "session_metadata", 
                    "description": "Session identifiers and timestamps",
                    "retention_days": settings.DATA_RETENTION_DAYS,
                    "legal_basis": "Legitimate interest"
                },
                {
                    "category": "usage_analytics",
                    "description": "Anonymized usage statistics",
                    "retention_days": 365,
                    "legal_basis": "Legitimate interest"
                }
            ],
            "pseudonymization": True,
            "encryption": True,
            "data_residency": "EU (Sweden)"
        }
        
    except Exception as e:
        logger.error(f"Data categories error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get data categories")
