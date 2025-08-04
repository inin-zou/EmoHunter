"""
🎵 Text-to-Speech Client Service

Service for ElevenLabs TTS integration with emotion-aware voice modulation.
"""

import base64
import os
from typing import Dict, Optional

from common.config import settings, get_emotion_voice_mapping
from common.utils.logger import get_service_logger
from common.utils.helpers import encode_audio_to_base64

logger = get_service_logger("tts_client")

# Try to import ElevenLabs with proper version handling
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import Voice, VoiceSettings
    ELEVENLABS_AVAILABLE = True
    logger.info("✅ ElevenLabs v2+ API loaded successfully")
except ImportError:
    try:
        from elevenlabs import generate, set_api_key
        ELEVENLABS_AVAILABLE = "v1"
        logger.info("✅ ElevenLabs v1 API loaded successfully")
    except ImportError:
        logger.warning("⚠️ ElevenLabs library not available. Voice generation will be disabled.")
        ELEVENLABS_AVAILABLE = False


class TTSClient:
    """
    🎵 Text-to-Speech Client Service
    
    Handles emotion-aware voice synthesis using ElevenLabs API
    """
    
    def __init__(self):
        """Initialize the TTS client"""
        self.api_key = settings.elevenlabs_api_key
        self.emotion_voice_mapping = get_emotion_voice_mapping()
        
        # Initialize ElevenLabs client
        if ELEVENLABS_AVAILABLE == True and self.api_key:
            self.client = ElevenLabs(api_key=self.api_key)
            logger.info("🎵 ElevenLabs v2+ client initialized")
        elif ELEVENLABS_AVAILABLE == "v1" and self.api_key:
            set_api_key(self.api_key)
            self.client = "v1"
            logger.info("🎵 ElevenLabs v1 client initialized")
        else:
            self.client = None
            if not self.api_key:
                logger.warning("⚠️ ElevenLabs API key not configured")
            else:
                logger.warning("⚠️ ElevenLabs library not available")
        
        logger.info("🎵 TTS Client initialized")
    
    def synthesize_speech(self, text: str, emotion: Optional[str] = "neutral", voice_settings: Optional[Dict] = None) -> Dict:
        """
        Synthesize speech with emotion-appropriate tone
        
        Args:
            text: Text to synthesize
            emotion: Current emotional context for tone adjustment
            voice_settings: Optional custom voice settings
            
        Returns:
            Dict containing audio data and metadata
        """
        try:
            emotion = emotion or "neutral"
            voice_config = self.emotion_voice_mapping.get(emotion, self.emotion_voice_mapping["neutral"])
            
            # Override with custom settings if provided
            if voice_settings:
                voice_config.update(voice_settings)
            
            # Generate audio based on available API version
            audio_base64 = None
            duration_seconds = None
            
            if self.client == "v1":
                audio_base64 = self._synthesize_v1(text, voice_config)
            elif self.client:
                audio_base64 = self._synthesize_v2(text, voice_config)
            else:
                # Mock audio response
                audio_base64 = self._generate_mock_audio(text, emotion)
                logger.info(f"🎵 Mock voice synthesis: '{text[:50]}...' with {emotion} tone")
            
            return {
                "audio_data": audio_base64,
                "text": text,
                "emotion": emotion,
                "voice_config": voice_config,
                "duration_seconds": duration_seconds,
                "audio_format": "mp3"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in voice synthesis: {e}")
            raise Exception(f"Voice synthesis failed: {str(e)}")
    
    def _synthesize_v1(self, text: str, voice_config: Dict) -> str:
        """Synthesize using ElevenLabs v1 API"""
        try:
            audio = generate(
                text=text,
                voice=voice_config["voice"],
                model="eleven_monolingual_v1"
            )
            return base64.b64encode(audio).decode()
        except Exception as e:
            logger.error(f"❌ ElevenLabs v1 synthesis error: {e}")
            raise Exception(f"ElevenLabs v1 synthesis failed: {str(e)}")
    
    def _synthesize_v2(self, text: str, voice_config: Dict) -> str:
        """Synthesize using ElevenLabs v2+ API"""
        try:
            voice = Voice(
                voice_id=voice_config["voice"],
                settings=VoiceSettings(
                    stability=voice_config["stability"],
                    similarity_boost=voice_config["similarity_boost"]
                )
            )
            
            audio = self.client.generate(
                text=text,
                voice=voice,
                model="eleven_monolingual_v1"
            )
            
            # Convert generator to bytes and encode
            audio_bytes = b"".join(audio)
            return base64.b64encode(audio_bytes).decode()
            
        except Exception as e:
            logger.error(f"❌ ElevenLabs v2+ synthesis error: {e}")
            raise Exception(f"ElevenLabs v2+ synthesis failed: {str(e)}")
    
    def _generate_mock_audio(self, text: str, emotion: str) -> str:
        """Generate mock audio data for development"""
        # Create a simple mock base64 string that represents audio
        mock_data = f"mock_audio_{emotion}_{len(text)}_bytes"
        return base64.b64encode(mock_data.encode()).decode()
    
    def get_available_voices(self) -> Dict:
        """Get available voice configurations"""
        return self.emotion_voice_mapping.copy()
    
    def validate_voice_settings(self, voice_settings: Dict) -> bool:
        """Validate voice configuration parameters"""
        try:
            # Check stability range
            if "stability" in voice_settings and not (0.0 <= voice_settings["stability"] <= 1.0):
                return False
            
            # Check similarity_boost range
            if "similarity_boost" in voice_settings and not (0.0 <= voice_settings["similarity_boost"] <= 1.0):
                return False
            
            # Check voice name is not empty
            if "voice" in voice_settings and (not voice_settings["voice"] or not voice_settings["voice"].strip()):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Voice settings validation error: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Get TTS client status information"""
        return {
            "status": "active" if self.client else "disabled",
            "api_configured": bool(self.api_key),
            "api_version": ELEVENLABS_AVAILABLE,
            "available_emotions": list(self.emotion_voice_mapping.keys()),
            "default_voice": settings.default_voice,
            "mock_mode": not bool(self.client)
        }
    
    def test_synthesis(self, test_text: str = "Hello, this is a test.") -> bool:
        """Test voice synthesis functionality"""
        try:
            result = self.synthesize_speech(test_text, "neutral")
            return bool(result.get("audio_data"))
            
        except Exception as e:
            logger.error(f"❌ Voice synthesis test failed: {e}")
            return False
