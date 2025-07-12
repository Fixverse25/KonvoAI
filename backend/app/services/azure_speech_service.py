"""
Azure Speech Service - Swedish Optimized
Handles speech-to-text and text-to-speech operations using Azure Cognitive Services
Optimized for Swedish language and EV charging terminology
"""

import asyncio
import io
import tempfile
import aiohttp
import base64
from typing import Optional, AsyncGenerator
import azure.cognitiveservices.speech as speechsdk
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AzureSpeechService:
    """Azure Speech Service optimized for Swedish EV charging support"""

    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=settings.azure_speech_key,
            region=settings.azure_speech_region
        )

        # Swedish language configuration
        self.speech_config.speech_recognition_language = getattr(settings, 'azure_speech_language', 'sv-SE')
        self.speech_config.speech_synthesis_voice_name = getattr(settings, 'azure_speech_voice', 'sv-SE-SofiaNeural')

        # Swedish EV charging terminology for better recognition
        self.ev_phrase_list = [
            "elbil", "elbilen", "elbilar", "elbilarna",
            "laddstation", "laddstationen", "laddstationer", "laddstationerna",
            "laddkabel", "laddkabeln", "laddkablar", "laddkablarna",
            "snabbladdning", "snabbladdningen", "AC-laddning", "DC-laddning",
            "CCS", "CHAdeMO", "Type 2", "Tesla", "Supercharger",
            "kilowatt", "kW", "kilowattimme", "kWh", "batteri", "räckvidd",
            "hemmaladdning", "offentlig laddning", "laddtid", "laddningshastighet"
        ]

        # Configure for Swedish conversation mode
        # Note: Using available property for recognition mode
        try:
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_RecognitionMode,
                "conversation"
            )
        except AttributeError:
            # Property not available in this SDK version, skip
            pass

        # Enable detailed output for better accuracy
        self.speech_config.output_format = speechsdk.OutputFormat.Detailed

        # Configure timeouts for Swedish speech patterns
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs,
            "5000"
        )
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
            str(getattr(settings, 'silence_timeout_seconds', 3) * 1000)
        )

        # Set profanity handling
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceResponse_ProfanityOption,
            "Masked"
        )

        logger.info(f"Azure Speech configured for Swedish (region: {settings.azure_speech_region})")
    
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
            # Create speech synthesizer with file output (Docker-compatible)
            import tempfile
            import os

            # Create temporary file for audio output
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file.close()

            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file.name)
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            # Perform synthesis
            result = speech_synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"Speech synthesized for text: {text[:50]}...")

                # Read audio data from temporary file
                try:
                    with open(temp_file.name, 'rb') as f:
                        audio_data = f.read()
                    os.unlink(temp_file.name)  # Clean up temp file
                    return audio_data
                except Exception as e:
                    logger.error(f"Failed to read temp audio file: {e}")
                    os.unlink(temp_file.name)  # Clean up temp file
                    return result.audio_data
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                logger.error(f"Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.error_details:
                    logger.error(f"Error details: {cancellation_details.error_details}")
                # Clean up temp file
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                return None

        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
            return None
    
    async def test_connection(self) -> bool:
        """Test Azure Speech Service connection"""
        try:
            # Create a simple test synthesis with file output
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file.close()

            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file.name)
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            result = speech_synthesizer.speak_text_async("Test").get()

            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info("Azure Speech Service connection test successful")
                return True
            else:
                logger.error("Azure Speech Service connection test failed")
                return False

        except Exception as e:
            logger.error(f"Azure Speech Service connection test error: {e}")
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
            return False

    async def text_to_speech_rest_api(self, text: str) -> Optional[bytes]:
        """
        Fallback text-to-speech using Azure Speech REST API
        Used when SDK platform initialization fails in Docker
        """
        try:
            # Try different endpoint format
            url = f"https://{settings.azure_speech_region}.api.cognitive.microsoft.com/sts/v1.0/issuetoken"

            # First get access token
            token_headers = {
                'Ocp-Apim-Subscription-Key': settings.azure_speech_key,
                'Content-Length': '0'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=token_headers) as token_response:
                    if token_response.status != 200:
                        logger.error(f"Failed to get access token: {token_response.status}")
                        return None

                    access_token = await token_response.text()

                    # Now use the token for TTS
                    tts_url = f"https://{settings.azure_speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"

                    tts_headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/ssml+xml',
                        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3'
                    }

                    # SSML for Swedish voice - clean format without extra whitespace
                    import html
                    escaped_text = html.escape(text)
                    # Try with specific Swedish voice
                    ssml = f'<speak version="1.0" xml:lang="sv-SE"><voice xml:lang="sv-SE" name="sv-SE-SofiaNeural">{escaped_text}</voice></speak>'

                    async with session.post(tts_url, headers=tts_headers, data=ssml) as response:
                        if response.status == 200:
                            audio_data = await response.read()
                            logger.info(f"REST API speech synthesized for text: {text[:50]}...")
                            return audio_data
                        else:
                            error_text = await response.text()
                            logger.error(f"REST API TTS failed with status: {response.status}, error: {error_text}")
                            logger.error(f"Request URL: {tts_url}")
                            logger.error(f"Request headers: {tts_headers}")
                            logger.error(f"Request SSML: {ssml}")
                            return None

        except Exception as e:
            logger.error(f"REST API text-to-speech error: {e}")
            return None

    async def text_to_speech_with_fallback(self, text: str) -> Optional[bytes]:
        """
        Text-to-speech with automatic fallback to REST API
        """
        # Try SDK first
        try:
            result = await self.text_to_speech(text)
            if result:
                return result
        except Exception as e:
            logger.warning(f"SDK TTS failed, trying REST API fallback: {e}")

        # Fallback to REST API
        return await self.text_to_speech_rest_api(text)


# Global Azure Speech Service instance
azure_speech_service = AzureSpeechService()
