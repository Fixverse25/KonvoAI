"""
Chat Data Models
Pydantic models for chat-related data structures
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Message type enumeration"""
    TEXT = "text"
    VOICE = "voice"


class ChatMessage(BaseModel):
    """Chat message model"""
    id: str = Field(..., description="Unique message identifier")
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    session_id: str = Field(..., description="Session identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ChatSession(BaseModel):
    """Chat session model"""
    id: str = Field(..., description="Unique session identifier")
    messages: List[ChatMessage] = Field(default=[], description="Session messages")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Session metadata")


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    stream: bool = Field(default=False, description="Enable streaming response")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session identifier")
    message_id: str = Field(..., description="Response message identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Response metadata")


class VoiceRequest(BaseModel):
    """Voice request model"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    format: str = Field(default="wav", description="Audio format")
    language: Optional[str] = Field(default=None, description="Audio language")


class VoiceResponse(BaseModel):
    """Voice response model"""
    transcription: str = Field(..., description="Speech-to-text transcription")
    response_text: str = Field(..., description="AI response text")
    response_audio: str = Field(..., description="Base64 encoded response audio")
    session_id: str = Field(..., description="Session identifier")
    message_id: str = Field(..., description="Response message identifier")
    confidence: Optional[float] = Field(default=None, description="Transcription confidence")


class TTSRequest(BaseModel):
    """Text-to-speech request model"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    voice: Optional[str] = Field(default=None, description="Voice identifier")
    language: Optional[str] = Field(default=None, description="Language code")
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")


class STTResponse(BaseModel):
    """Speech-to-text response model"""
    transcription: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Transcription confidence")
    language: str = Field(..., description="Detected language")
    duration: Optional[float] = Field(default=None, description="Audio duration in seconds")


class HealthStatus(BaseModel):
    """Health status model"""
    status: str = Field(..., description="Overall health status")
    environment: str = Field(..., description="Environment name")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    services: Optional[Dict[str, str]] = Field(default=None, description="Service statuses")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
