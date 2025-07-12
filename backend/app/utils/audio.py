"""
Audio Utility Functions
Helper functions for audio processing and conversion
"""

import io
import base64
import tempfile
from typing import Optional, Tuple
from pydub import AudioSegment
import numpy as np
from app.core.logging import get_logger

logger = get_logger(__name__)


def convert_audio_format(
    audio_data: bytes,
    input_format: str,
    output_format: str = "wav",
    sample_rate: int = 16000,
    channels: int = 1
) -> Optional[bytes]:
    """
    Convert audio from one format to another
    
    Args:
        audio_data: Input audio bytes
        input_format: Input audio format (e.g., 'webm', 'mp3', 'wav')
        output_format: Output audio format (default: 'wav')
        sample_rate: Target sample rate (default: 16000)
        channels: Target number of channels (default: 1)
        
    Returns:
        Converted audio bytes or None if conversion failed
    """
    try:
        # Load audio data with fallback for WebM
        if input_format.lower() == 'webm':
            # Try WebM first, fallback to OGG
            try:
                audio = AudioSegment.from_file(
                    io.BytesIO(audio_data),
                    format='webm'
                )
            except Exception:
                logger.warning("WebM decode failed, trying OGG format")
                audio = AudioSegment.from_file(
                    io.BytesIO(audio_data),
                    format='ogg'
                )
        else:
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data),
                format=input_format
            )
        
        # Convert to target format
        audio = audio.set_frame_rate(sample_rate)
        audio = audio.set_channels(channels)
        
        # Export to bytes
        output_buffer = io.BytesIO()
        audio.export(output_buffer, format=output_format)
        
        logger.info(f"Audio converted from {input_format} to {output_format}")
        return output_buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        return None


def validate_audio_data(audio_data: bytes, max_size_mb: int = 10) -> bool:
    """
    Validate audio data
    
    Args:
        audio_data: Audio bytes to validate
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check size
        size_mb = len(audio_data) / (1024 * 1024)
        if size_mb > max_size_mb:
            logger.warning(f"Audio file too large: {size_mb:.2f}MB > {max_size_mb}MB")
            return False
        
        # Try to load audio to validate format
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        
        # Check duration (max 60 seconds)
        duration_seconds = len(audio) / 1000
        if duration_seconds > 60:
            logger.warning(f"Audio too long: {duration_seconds:.2f}s > 60s")
            return False
        
        logger.info(f"Audio validation passed: {size_mb:.2f}MB, {duration_seconds:.2f}s")
        return True
        
    except Exception as e:
        logger.error(f"Audio validation failed: {e}")
        return False


def get_audio_info(audio_data: bytes) -> Optional[dict]:
    """
    Get audio file information
    
    Args:
        audio_data: Audio bytes
        
    Returns:
        Dictionary with audio info or None if failed
    """
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        
        info = {
            "duration_seconds": len(audio) / 1000,
            "sample_rate": audio.frame_rate,
            "channels": audio.channels,
            "sample_width": audio.sample_width,
            "frame_count": audio.frame_count(),
            "size_bytes": len(audio_data),
            "size_mb": len(audio_data) / (1024 * 1024),
        }
        
        logger.info(f"Audio info extracted: {info}")
        return info
        
    except Exception as e:
        logger.error(f"Failed to get audio info: {e}")
        return None


def normalize_audio_volume(audio_data: bytes, target_dBFS: float = -20.0) -> Optional[bytes]:
    """
    Normalize audio volume
    
    Args:
        audio_data: Input audio bytes
        target_dBFS: Target volume in dBFS
        
    Returns:
        Normalized audio bytes or None if failed
    """
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        
        # Calculate volume change needed
        change_in_dBFS = target_dBFS - audio.dBFS
        
        # Apply volume change
        normalized_audio = audio.apply_gain(change_in_dBFS)
        
        # Export to bytes
        output_buffer = io.BytesIO()
        normalized_audio.export(output_buffer, format="wav")
        
        logger.info(f"Audio volume normalized: {audio.dBFS:.2f} -> {target_dBFS:.2f} dBFS")
        return output_buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Audio normalization failed: {e}")
        return None


def detect_silence_segments(
    audio_data: bytes,
    silence_threshold: float = -40.0,
    min_silence_duration: int = 1000
) -> list:
    """
    Detect silence segments in audio
    
    Args:
        audio_data: Input audio bytes
        silence_threshold: Silence threshold in dBFS
        min_silence_duration: Minimum silence duration in milliseconds
        
    Returns:
        List of silence segments [(start_ms, end_ms), ...]
    """
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        
        # Detect silence
        silence_segments = []
        silence_start = None
        
        # Analyze audio in chunks
        chunk_size = 100  # 100ms chunks
        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            
            if chunk.dBFS < silence_threshold:
                if silence_start is None:
                    silence_start = i
            else:
                if silence_start is not None:
                    silence_duration = i - silence_start
                    if silence_duration >= min_silence_duration:
                        silence_segments.append((silence_start, i))
                    silence_start = None
        
        # Handle silence at the end
        if silence_start is not None:
            silence_duration = len(audio) - silence_start
            if silence_duration >= min_silence_duration:
                silence_segments.append((silence_start, len(audio)))
        
        logger.info(f"Detected {len(silence_segments)} silence segments")
        return silence_segments
        
    except Exception as e:
        logger.error(f"Silence detection failed: {e}")
        return []


def trim_silence(
    audio_data: bytes,
    silence_threshold: float = -40.0,
    padding_ms: int = 100
) -> Optional[bytes]:
    """
    Trim silence from beginning and end of audio
    
    Args:
        audio_data: Input audio bytes
        silence_threshold: Silence threshold in dBFS
        padding_ms: Padding to keep in milliseconds
        
    Returns:
        Trimmed audio bytes or None if failed
    """
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        
        # Find first non-silent chunk
        start_trim = 0
        chunk_size = 100
        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            if chunk.dBFS > silence_threshold:
                start_trim = max(0, i - padding_ms)
                break
        
        # Find last non-silent chunk
        end_trim = len(audio)
        for i in range(len(audio) - chunk_size, 0, -chunk_size):
            chunk = audio[i:i + chunk_size]
            if chunk.dBFS > silence_threshold:
                end_trim = min(len(audio), i + chunk_size + padding_ms)
                break
        
        # Trim audio
        trimmed_audio = audio[start_trim:end_trim]
        
        # Export to bytes
        output_buffer = io.BytesIO()
        trimmed_audio.export(output_buffer, format="wav")
        
        original_duration = len(audio) / 1000
        trimmed_duration = len(trimmed_audio) / 1000
        logger.info(f"Audio trimmed: {original_duration:.2f}s -> {trimmed_duration:.2f}s")
        
        return output_buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Audio trimming failed: {e}")
        return None


def base64_to_audio_bytes(base64_data: str) -> Optional[bytes]:
    """
    Convert base64 string to audio bytes
    
    Args:
        base64_data: Base64 encoded audio data
        
    Returns:
        Audio bytes or None if conversion failed
    """
    try:
        audio_bytes = base64.b64decode(base64_data)
        logger.info(f"Converted base64 to {len(audio_bytes)} bytes")
        return audio_bytes
    except Exception as e:
        logger.error(f"Base64 to audio conversion failed: {e}")
        return None


def audio_bytes_to_base64(audio_bytes: bytes) -> Optional[str]:
    """
    Convert audio bytes to base64 string
    
    Args:
        audio_bytes: Audio bytes
        
    Returns:
        Base64 encoded string or None if conversion failed
    """
    try:
        base64_data = base64.b64encode(audio_bytes).decode('utf-8')
        logger.info(f"Converted {len(audio_bytes)} bytes to base64")
        return base64_data
    except Exception as e:
        logger.error(f"Audio to base64 conversion failed: {e}")
        return None
