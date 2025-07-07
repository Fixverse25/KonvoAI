"""
EVA-Dev Configuration Management
Handles all application settings and environment variables
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # =============================================================================
    # Application Settings
    # =============================================================================
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    secret_key: str = Field(..., env="SECRET_KEY")
    
    # =============================================================================
    # Azure Speech Services
    # =============================================================================
    azure_speech_key: str = Field(..., env="AZURE_SPEECH_KEY")
    azure_speech_region: str = Field(..., env="AZURE_SPEECH_REGION")
    azure_speech_language: str = Field(default="en-US", env="AZURE_SPEECH_LANGUAGE")
    azure_speech_voice: str = Field(default="en-US-AriaNeural", env="AZURE_SPEECH_VOICE")
    
    # =============================================================================
    # Anthropic Claude API
    # =============================================================================
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    claude_model: str = Field(default="claude-3-sonnet-20240229", env="CLAUDE_MODEL")
    claude_max_tokens: int = Field(default=4000, env="CLAUDE_MAX_TOKENS")
    
    # =============================================================================
    # CORS and Security
    # =============================================================================
    allowed_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
            "file://",
            "null"  # For file:// protocol
        ],
        env="ALLOWED_ORIGINS"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1", "fixverse.se", "api.fixverse.se"],
        env="ALLOWED_HOSTS"
    )
    
    # =============================================================================
    # Audio Settings
    # =============================================================================
    max_audio_duration_seconds: int = Field(default=30, env="MAX_AUDIO_DURATION_SECONDS")
    silence_timeout_seconds: int = Field(default=3, env="SILENCE_TIMEOUT_SECONDS")
    audio_sample_rate: int = Field(default=16000, env="AUDIO_SAMPLE_RATE")
    
    # =============================================================================
    # Rate Limiting
    # =============================================================================
    rate_limit_requests_per_minute: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    
    # =============================================================================
    # Redis Configuration
    # =============================================================================
    redis_url: str = Field(default="redis://redis:6379/0", env="REDIS_URL")
    
    # =============================================================================
    # Database Configuration (Optional)
    # =============================================================================
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    @validator("allowed_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment"""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v.lower()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
