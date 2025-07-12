"""
Voice API Endpoints
Handles voice interactions including speech-to-text and text-to-speech
"""

import uuid
import base64
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.azure_speech_service import azure_speech_service
from app.services.claude_service import claude_service
from app.services.redis_service import redis_service
from app.utils.audio import (
    convert_audio_format,
    validate_audio_data,
    get_audio_info,
    normalize_audio_volume,
    trim_silence,
    base64_to_audio_bytes,
    audio_bytes_to_base64
)

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


class VoiceRequest(BaseModel):
    """Voice request model"""
    audio_data: str  # Base64 encoded audio
    session_id: str = None
    format: str = "wav"  # Audio format


class VoiceResponse(BaseModel):
    """Voice response model"""
    transcription: str
    response_text: str
    response_audio: str  # Base64 encoded audio
    session_id: str
    message_id: str


class TTSRequest(BaseModel):
    """Text-to-speech request model"""
    text: str
    voice: str = None


@router.post("/speech-to-text")
@limiter.limit(f"{settings.rate_limit_requests_per_minute}/minute")
async def speech_to_text(
    request: Request,
    audio_file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Convert speech audio to text using Azure Speech Services
    """
    try:
        # Validate file type
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file type")
        
        # Read audio data
        audio_data = await audio_file.read()

        # Validate audio data
        if not validate_audio_data(audio_data, max_size_mb=10):
            raise HTTPException(status_code=400, detail="Invalid or too large audio file")

        # Get audio info for logging
        audio_info = get_audio_info(audio_data)
        if audio_info:
            logger.info(f"Processing audio: {audio_info}")

        # Convert to WAV format if needed
        if not audio_file.content_type.endswith('wav'):
            # Detect format from content type
            input_format = audio_file.content_type.split('/')[-1]
            if input_format in ['webm', 'ogg']:
                input_format = 'webm'

            converted_audio = convert_audio_format(
                audio_data,
                input_format=input_format,
                output_format='wav',
                sample_rate=16000,
                channels=1
            )

            if converted_audio:
                audio_data = converted_audio
            else:
                logger.warning("Audio conversion failed, using original data")

        # Normalize and trim audio
        normalized_audio = normalize_audio_volume(audio_data)
        if normalized_audio:
            audio_data = normalized_audio

        trimmed_audio = trim_silence(audio_data)
        if trimmed_audio:
            audio_data = trimmed_audio

        # Convert speech to text
        transcription = await azure_speech_service.speech_to_text(audio_data)
        
        if not transcription:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        logger.info(f"Speech transcribed: {transcription[:50]}...")
        
        return {
            "transcription": transcription,
            "confidence": 1.0,  # Azure doesn't provide confidence in basic API
            "language": settings.azure_speech_language
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        raise HTTPException(status_code=500, detail="Speech recognition failed")


@router.post("/text-to-speech")
@limiter.limit(f"{settings.rate_limit_requests_per_minute}/minute")
async def text_to_speech(
    request: Request,
    tts_request: TTSRequest
) -> Response:
    """
    Convert text to speech using Azure Speech Services
    """
    try:
        # Validate text length
        if len(tts_request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long for synthesis")
        
        # Convert text to speech with fallback
        audio_data = await azure_speech_service.text_to_speech_with_fallback(tts_request.text)
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="Speech synthesis failed")
        
        logger.info(f"Text synthesized: {tts_request.text[:50]}...")
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}")
        raise HTTPException(status_code=500, detail="Speech synthesis failed")


@router.post("/voice-chat", response_model=VoiceResponse)
@limiter.limit(f"{settings.rate_limit_requests_per_minute}/minute")
async def voice_chat(
    request: Request,
    voice_request: VoiceRequest
) -> VoiceResponse:
    """
    Complete voice interaction: speech-to-text, chat with Claude, text-to-speech
    """
    try:
        # Generate session ID if not provided
        session_id = voice_request.session_id or str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        # Decode audio data
        audio_data = base64_to_audio_bytes(voice_request.audio_data)
        if not audio_data:
            raise HTTPException(status_code=400, detail="Invalid audio data encoding")

        # Validate and process audio
        if not validate_audio_data(audio_data, max_size_mb=10):
            raise HTTPException(status_code=400, detail="Invalid or too large audio file")

        # Convert from WebM to WAV if needed
        if voice_request.format.lower() in ['webm', 'ogg']:
            converted_audio = convert_audio_format(
                audio_data,
                input_format='webm',
                output_format='wav',
                sample_rate=16000,
                channels=1
            )
            if converted_audio:
                audio_data = converted_audio

        # Enhance audio quality
        normalized_audio = normalize_audio_volume(audio_data)
        if normalized_audio:
            audio_data = normalized_audio

        trimmed_audio = trim_silence(audio_data)
        if trimmed_audio:
            audio_data = trimmed_audio
        
        # Step 1: Convert speech to text
        transcription = await azure_speech_service.speech_to_text(audio_data)
        if not transcription:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # Step 2: Get conversation history and add user message
        conversation_key = f"conversation:{session_id}"
        conversation_history = await redis_service.get(conversation_key) or []
        
        user_message = {
            "role": "user",
            "content": transcription,
            "timestamp": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "type": "voice"
        }
        conversation_history.append(user_message)
        
        # Step 3: Get response from Claude
        claude_messages = claude_service.format_conversation_history(conversation_history)
        response_text = await claude_service.chat_completion(claude_messages)
        
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to get AI response")
        
        # Step 4: Convert response to speech with fallback
        response_audio_data = await azure_speech_service.text_to_speech_with_fallback(response_text)
        if not response_audio_data:
            raise HTTPException(status_code=500, detail="Failed to synthesize speech")
        
        # Step 5: Save assistant response to history
        assistant_message = {
            "role": "assistant",
            "content": response_text,
            "timestamp": str(uuid.uuid4()),
            "message_id": message_id,
            "type": "voice"
        }
        conversation_history.append(assistant_message)
        
        # Save updated conversation to Redis
        await redis_service.set(conversation_key, conversation_history, expire=3600)
        
        # Encode response audio to base64
        response_audio_b64 = audio_bytes_to_base64(response_audio_data)
        if not response_audio_b64:
            raise HTTPException(status_code=500, detail="Failed to encode response audio")
        
        logger.info(f"Voice chat completed for session {session_id}")
        
        return VoiceResponse(
            transcription=transcription,
            response_text=response_text,
            response_audio=response_audio_b64,
            session_id=session_id,
            message_id=message_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        raise HTTPException(status_code=500, detail="Voice chat failed")


@router.get("/test-services")
@limiter.limit("10/minute")
async def test_voice_services(request: Request) -> Dict[str, Any]:
    """
    Test voice services connectivity
    """
    try:
        # Test Azure Speech Service
        azure_test = await azure_speech_service.test_connection()
        
        # Test Claude API
        claude_test = await claude_service.test_connection()
        
        return {
            "azure_speech": "healthy" if azure_test else "unhealthy",
            "claude_api": "healthy" if claude_test else "unhealthy",
            "overall_status": "healthy" if (azure_test and claude_test) else "degraded"
        }
        
    except Exception as e:
        logger.error(f"Service test error: {e}")
        return {
            "azure_speech": "error",
            "claude_api": "error",
            "overall_status": "unhealthy",
            "error": str(e)
        }
