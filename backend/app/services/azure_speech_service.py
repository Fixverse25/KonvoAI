"""
Azure Speech Service
Handles speech-to-text and text-to-speech operations using Azure Cognitive Services
"""

import asyncio
import io
import tempfile
from typing import Optional, AsyncGenerator
import azure.cognitiveservices.speech as speechsdk
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AzureSpeechService:
    """Azure Speech Service for STT and TTS operations"""
    
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=settings.azure_speech_key,
            region=settings.azure_speech_region
        )
        self.speech_config.speech_recognition_language = settings.azure_speech_language
        self.speech_config.speech_synthesis_voice_name = settings.azure_speech_voice
        
        # Configure audio format for better quality
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, 
            "5000"
        )
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
            str(settings.silence_timeout_seconds * 1000)
        )
    
    async def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """
        Convert speech audio to text
        
        Args:
            audio_data: Raw audio bytes (WAV format)
            
        Returns:
            Transcribed text or None if recognition failed
        """
        try:
            # Create audio stream from bytes
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
            
            # Create speech recognizer
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Push audio data to stream
            audio_stream.write(audio_data)
            audio_stream.close()
            
            # Perform recognition
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                logger.info(f"Speech recognized: {result.text}")
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech could be recognized")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                logger.error(f"Speech recognition canceled: {cancellation_details.reason}")
                if cancellation_details.error_details:
                    logger.error(f"Error details: {cancellation_details.error_details}")
                return None
            
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            return None
    
    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech audio
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes (WAV format) or None if synthesis failed
        """
        try:
            # Create speech synthesizer with memory stream
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Perform synthesis
            result = speech_synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"Speech synthesized for text: {text[:50]}...")
                return result.audio_data
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                logger.error(f"Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.error_details:
                    logger.error(f"Error details: {cancellation_details.error_details}")
                return None
            
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            return None
    
    async def test_connection(self) -> bool:
        """Test Azure Speech Service connection"""
        try:
            # Create a simple test synthesis
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            result = speech_synthesizer.speak_text_async("Test").get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info("Azure Speech Service connection test successful")
                return True
            else:
                logger.error("Azure Speech Service connection test failed")
                return False
                
        except Exception as e:
            logger.error(f"Azure Speech Service connection test error: {e}")
            return False


# Global Azure Speech Service instance
azure_speech_service = AzureSpeechService()
