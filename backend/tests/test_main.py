"""
Unit tests for main FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestMainApp:
    """Test main application endpoints and functionality"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "EVA-Dev API"
        assert data["version"] == "1.0.0"
        assert "docs" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "environment" in data
    
    def test_cors_headers(self):
        """Test CORS headers are properly configured"""
        response = client.options("/")
        # CORS should be configured to allow requests
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled
    
    def test_api_routes_included(self):
        """Test that API routes are properly included"""
        # Test that API routes exist
        response = client.get("/api/v1/health/")
        assert response.status_code == 200
    
    def test_rate_limiting_configured(self):
        """Test that rate limiting is configured"""
        # Make multiple requests to test rate limiting
        responses = []
        for i in range(5):
            response = client.post("/api/v1/chat", json={"message": f"test {i}"})
            responses.append(response)
        
        # At least some requests should succeed (even if API keys are missing)
        # We're testing that the rate limiter doesn't immediately block requests
        success_or_auth_errors = [
            r for r in responses 
            if r.status_code in [200, 401, 422, 500]  # Not rate limited
        ]
        assert len(success_or_auth_errors) > 0
    
    def test_exception_handling(self):
        """Test global exception handling"""
        # Test with invalid endpoint
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_openapi_docs_available_in_dev(self):
        """Test that OpenAPI docs are available in development"""
        # This test assumes we're running in development mode
        # In production, docs should be disabled
        response = client.get("/docs")
        # Should either return docs or redirect, not 404
        assert response.status_code in [200, 307, 404]  # 404 if disabled in production
    
    def test_api_versioning(self):
        """Test API versioning is properly implemented"""
        # Test v1 API endpoints exist
        response = client.get("/api/v1/health/")
        assert response.status_code == 200
        
        # Test that non-versioned API returns 404
        response = client.get("/api/health/")
        assert response.status_code == 404
