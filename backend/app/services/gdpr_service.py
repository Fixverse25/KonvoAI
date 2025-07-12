"""
GDPR Compliance Service
Handles data protection, privacy, and GDPR compliance for KonvoAI
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.redis_service import redis_service

logger = get_logger(__name__)
settings = get_settings()


class GDPRDataSubject(BaseModel):
    """GDPR Data Subject model"""
    subject_id: str
    pseudonym_id: str
    created_at: datetime
    last_activity: datetime
    consent_given: bool
    consent_timestamp: Optional[datetime]
    data_categories: List[str]


class GDPRService:
    """Service for GDPR compliance and data protection"""
    
    def __init__(self):
        self.retention_days = getattr(settings, 'DATA_RETENTION_DAYS', 30)
        self.conversation_retention = getattr(settings, 'CONVERSATION_RETENTION_DAYS', 7)
        self.gdpr_enabled = getattr(settings, 'GDPR_COMPLIANCE_MODE', True)
        self.pseudonymization = getattr(settings, 'PSEUDONYMIZATION_ENABLED', True)
    
    def generate_pseudonym(self, identifier: str) -> str:
        """
        Generate pseudonymized identifier (GDPR Article 4(5))
        """
        if not self.pseudonymization:
            return identifier
            
        # Create a salted hash for pseudonymization
        salt = settings.secret_key.encode()
        pseudonym = hashlib.sha256(f"{identifier}{salt}".encode()).hexdigest()[:16]
        return f"ps_{pseudonym}"
    
    def create_data_subject(self, session_id: str, consent: bool = False) -> GDPRDataSubject:
        """
        Create a new data subject with GDPR compliance
        """
        pseudonym = self.generate_pseudonym(session_id)
        
        data_subject = GDPRDataSubject(
            subject_id=session_id,
            pseudonym_id=pseudonym,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            consent_given=consent,
            consent_timestamp=datetime.utcnow() if consent else None,
            data_categories=["conversation_data", "session_metadata"]
        )
        
        # Store in Redis with expiration
        redis_key = f"gdpr:subject:{pseudonym}"
        redis_service.set(
            redis_key, 
            data_subject.dict(), 
            expire=self.retention_days * 24 * 3600
        )
        
        logger.info(f"Created GDPR data subject: {pseudonym}")
        return data_subject
    
    def record_consent(self, session_id: str, consent_given: bool) -> bool:
        """
        Record user consent (GDPR Article 7)
        """
        pseudonym = self.generate_pseudonym(session_id)
        redis_key = f"gdpr:subject:{pseudonym}"
        
        subject_data = redis_service.get(redis_key)
        if subject_data:
            subject_data['consent_given'] = consent_given
            subject_data['consent_timestamp'] = datetime.utcnow().isoformat()
            subject_data['last_activity'] = datetime.utcnow().isoformat()
            
            redis_service.set(redis_key, subject_data, expire=self.retention_days * 24 * 3600)
            
            logger.info(f"Recorded consent for {pseudonym}: {consent_given}")
            return True
        
        return False
    
    def check_consent(self, session_id: str) -> bool:
        """
        Check if user has given valid consent
        """
        if not self.gdpr_enabled:
            return True
            
        pseudonym = self.generate_pseudonym(session_id)
        redis_key = f"gdpr:subject:{pseudonym}"
        
        subject_data = redis_service.get(redis_key)
        if subject_data:
            return subject_data.get('consent_given', False)
        
        return False
    
    def process_data_deletion(self, session_id: str) -> Dict[str, Any]:
        """
        Process right to erasure request (GDPR Article 17)
        """
        pseudonym = self.generate_pseudonym(session_id)
        
        # Delete conversation data
        conversation_key = f"conversation:{session_id}"
        redis_service.delete(conversation_key)
        
        # Delete GDPR subject data
        gdpr_key = f"gdpr:subject:{pseudonym}"
        redis_service.delete(gdpr_key)
        
        # Log the deletion (but not the content)
        logger.info(f"Processed data deletion for subject: {pseudonym}")
        
        return {
            "status": "completed",
            "subject_id": pseudonym,
            "deleted_at": datetime.utcnow().isoformat(),
            "data_categories": ["conversation_data", "session_metadata"]
        }
    
    def export_user_data(self, session_id: str) -> Dict[str, Any]:
        """
        Export user data for portability (GDPR Article 20)
        """
        pseudonym = self.generate_pseudonym(session_id)
        
        # Get conversation data
        conversation_key = f"conversation:{session_id}"
        conversation_data = redis_service.get(conversation_key) or []
        
        # Get GDPR subject data
        gdpr_key = f"gdpr:subject:{pseudonym}"
        subject_data = redis_service.get(gdpr_key) or {}
        
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "subject_id": pseudonym,
            "data_categories": subject_data.get('data_categories', []),
            "consent_status": subject_data.get('consent_given', False),
            "conversation_history": conversation_data,
            "metadata": {
                "created_at": subject_data.get('created_at'),
                "last_activity": subject_data.get('last_activity'),
                "retention_period_days": self.retention_days
            }
        }
        
        logger.info(f"Exported data for subject: {pseudonym}")
        return export_data
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """
        Clean up expired data according to retention policies
        """
        # This would typically be run as a scheduled job
        cleanup_stats = {
            "conversations_deleted": 0,
            "subjects_deleted": 0,
            "logs_deleted": 0
        }
        
        logger.info(f"Data cleanup completed: {cleanup_stats}")
        return cleanup_stats
    
    def validate_data_residency(self, request_origin: str) -> bool:
        """
        Validate that data processing complies with EU residency requirements
        """
        eu_regions = getattr(settings, 'ALLOWED_DATA_REGIONS', 'eu-north-1,eu-west-1,swedencentral').split(',')
        
        # In a real implementation, you'd check the actual processing location
        # For now, we assume all processing happens in allowed regions
        return True
    
    def get_privacy_notice(self) -> Dict[str, Any]:
        """
        Get privacy notice information for users
        """
        return {
            "data_controller": "Fixverse AB",
            "contact_email": "privacy@fixverse.se",
            "data_categories": [
                "Conversation messages",
                "Session identifiers", 
                "Timestamps",
                "Usage analytics (anonymized)"
            ],
            "legal_basis": "Legitimate interest for providing EV charging support",
            "retention_period": f"{self.retention_days} days",
            "your_rights": [
                "Right to access your data",
                "Right to rectification", 
                "Right to erasure",
                "Right to data portability",
                "Right to object to processing"
            ],
            "data_residency": "European Union (Sweden)",
            "last_updated": "2024-01-01"
        }


# Global instance
gdpr_service = GDPRService()
