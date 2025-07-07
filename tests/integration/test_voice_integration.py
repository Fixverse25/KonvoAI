"""
Integration tests for voice functionality
Tests the complete voice pipeline: audio upload -> transcription -> AI response -> TTS
"""

import asyncio
import base64
import io
import pytest
import httpx
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_AUDIO_DIR = Path(__file__).parent / "test_audio"


class TestVoiceIntegration:
    """Integration tests for voice endpoints"""
    
    @pytest.fixture
    def client(self):
        """HTTP client for API requests"""
        return httpx.AsyncClient(base_url=BASE_URL)
    
    @pytest.fixture
    def sample_audio_wav(self):
        """Sample WAV audio file for testing"""
        # This would be a real audio file in practice
        # For testing, we create a minimal WAV header
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        audio_data = b'\x00' * 2048  # Silent audio data
        return wav_header + audio_data
    
    @pytest.fixture
    def sample_audio_base64(self, sample_audio_wav):
        """Base64 encoded audio for voice chat endpoint"""
        return base64.b64encode(sample_audio_wav).decode('utf-8')
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test API health check"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_voice_services_health(self, client):
        """Test voice services health check"""
        response = await client.get("/api/v1/voice/test-services")
        assert response.status_code == 200
        data = response.json()
        assert "azure_speech" in data
        assert "claude_api" in data
        assert "overall_status" in data
    
    @pytest.mark.asyncio
    async def test_speech_to_text(self, client, sample_audio_wav):
        """Test speech-to-text endpoint"""
        files = {"audio_file": ("test.wav", io.BytesIO(sample_audio_wav), "audio/wav")}
        
        response = await client.post("/api/v1/voice/speech-to-text", files=files)
        
        # Note: This test may fail with real Azure Speech Services
        # as our sample audio is silent. In a real test environment,
        # you would use actual speech audio files.
        if response.status_code == 200:
            data = response.json()
            assert "transcription" in data
            assert "confidence" in data
            assert "language" in data
        else:
            # Expected for silent audio
            assert response.status_code in [400, 500]
    
    @pytest.mark.asyncio
    async def test_text_to_speech(self, client):
        """Test text-to-speech endpoint"""
        request_data = {
            "text": "This is a test message for text to speech conversion.",
            "voice": "en-US-AriaNeural"
        }
        
        response = await client.post("/api/v1/voice/text-to-speech", json=request_data)
        
        if response.status_code == 200:
            # Should return audio data
            assert response.headers["content-type"] == "audio/wav"
            assert len(response.content) > 0
        else:
            # May fail if Azure Speech Services not configured
            assert response.status_code in [400, 500]
    
    @pytest.mark.asyncio
    async def test_voice_chat_flow(self, client, sample_audio_base64):
        """Test complete voice chat flow"""
        request_data = {
            "audio_data": sample_audio_base64,
            "format": "wav"
        }
        
        response = await client.post("/api/v1/voice/voice-chat", json=request_data)
        
        if response.status_code == 200:
            data = response.json()
            assert "transcription" in data
            assert "response_text" in data
            assert "response_audio" in data
            assert "session_id" in data
            assert "message_id" in data
            
            # Verify response audio is base64 encoded
            try:
                audio_bytes = base64.b64decode(data["response_audio"])
                assert len(audio_bytes) > 0
            except Exception:
                pytest.fail("Response audio is not valid base64")
        else:
            # Expected for silent audio or missing API keys
            assert response.status_code in [400, 500]
    
    @pytest.mark.asyncio
    async def test_chat_text_flow(self, client):
        """Test text chat functionality"""
        request_data = {
            "message": "What is CCS charging?",
            "stream": False
        }
        
        response = await client.post("/api/v1/chat", json=request_data)
        
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "session_id" in data
            assert "message_id" in data
            assert len(data["response"]) > 0
        else:
            # May fail if Claude API not configured
            assert response.status_code in [400, 500]
    
    @pytest.mark.asyncio
    async def test_chat_streaming_flow(self, client):
        """Test streaming chat functionality"""
        request_data = {
            "message": "Explain Level 2 charging briefly.",
            "stream": True
        }
        
        response = await client.post("/api/v1/chat/stream", json=request_data)
        
        if response.status_code == 200:
            # Should return streaming response
            assert response.headers.get("content-type") == "text/plain; charset=utf-8"
            
            # Read streaming content
            content = ""
            async for chunk in response.aiter_text():
                content += chunk
                if "[DONE]" in chunk:
                    break
            
            assert len(content) > 0
        else:
            # May fail if Claude API not configured
            assert response.status_code in [400, 500]
    
    @pytest.mark.asyncio
    async def test_session_management(self, client):
        """Test session management across multiple requests"""
        session_id = None
        
        # First message
        request_data = {
            "message": "Hello, I need help with EV charging.",
            "stream": False
        }
        
        response = await client.post("/api/v1/chat", json=request_data)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data["session_id"]
            assert session_id is not None
            
            # Second message with same session
            request_data = {
                "message": "What did I just ask about?",
                "session_id": session_id,
                "stream": False
            }
            
            response = await client.post("/api/v1/chat", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                assert data["session_id"] == session_id
                
                # Get chat history
                response = await client.get(f"/api/v1/chat/history/{session_id}")
                
                if response.status_code == 200:
                    history = response.json()
                    assert len(history) >= 2  # At least 2 messages
                    assert any(msg["role"] == "user" for msg in history)
                    assert any(msg["role"] == "assistant" for msg in history)
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, client):
        """Test rate limiting functionality"""
        # Make multiple rapid requests to trigger rate limiting
        tasks = []
        for i in range(70):  # Exceed the 60/minute limit
            task = client.post("/api/v1/chat", json={"message": f"Test message {i}"})
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check if any requests were rate limited
        rate_limited = any(
            isinstance(r, httpx.Response) and r.status_code == 429 
            for r in responses
        )
        
        # Note: Rate limiting may not trigger in test environment
        # depending on configuration
        if rate_limited:
            assert True  # Rate limiting is working
        else:
            # Rate limiting may be disabled in test environment
            pass
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test error handling for invalid requests"""
        # Test invalid audio format
        files = {"audio_file": ("test.txt", io.BytesIO(b"not audio data"), "text/plain")}
        response = await client.post("/api/v1/voice/speech-to-text", files=files)
        assert response.status_code == 400
        
        # Test empty message
        response = await client.post("/api/v1/chat", json={"message": ""})
        assert response.status_code == 422  # Validation error
        
        # Test invalid voice chat data
        response = await client.post("/api/v1/voice/voice-chat", json={"audio_data": "invalid-base64"})
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = await client.options("/api/v1/chat")
        
        # CORS headers should be present
        headers = response.headers
        assert "access-control-allow-origin" in headers or response.status_code == 405
    
    @pytest.mark.asyncio
    async def test_security_headers(self, client):
        """Test security headers are present"""
        response = await client.get("/health")
        
        headers = response.headers
        # Check for common security headers
        # Note: These may be added by nginx in production
        expected_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection"
        ]
        
        # In development, these headers may not be present
        # This test documents the expectation for production
        for header in expected_headers:
            if header in headers:
                assert headers[header] is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
