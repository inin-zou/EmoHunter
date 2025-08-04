"""
🔧 Configuration Management

Centralized configuration for the EmoHunter backend application.
Manages API keys, database settings, and other environment variables.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application settings
    app_name: str = "EmoHunter API"
    app_description: str = "🎭 Emotion Analysis Engine + 🎤 Conversation Engine"
    version: str = "2.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Service ports
    conversation_engine_port: int = 8001
    emotion_analysis_port: int = 8002
    incentive_engine_port: int = 8003
    gateway_port: int = 8000
    
    # API Keys
    elevenlabs_api_key: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Camera settings
    camera_index: int = int(os.getenv("CAMERA_INDEX", "0"))
    emotion_update_interval: float = float(os.getenv("EMOTION_UPDATE_INTERVAL", "1.0"))
    
    # Emotion Analysis Engine settings
    emotion_stability_threshold: int = 2  # Frames needed for stable emotion
    emotion_confidence_threshold: float = 0.9  # High confidence override
    emotion_history_size: int = 5  # Number of emotions to keep in history
    
    # Conversation Engine settings
    conversation_history_size: int = 10  # Number of exchanges to keep
    default_voice: str = "Rachel"
    
    # Voice synthesis settings (simplified - single voice configuration)
    voice_stability: float = 0.70
    voice_similarity_boost: float = 0.80
    voice_style: float = 0.50
    
    # CORS settings
    cors_origins: list = ["*"]  # In production, specify your domain
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Database settings (for future use)
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def get_emotion_voice_mapping() -> dict:
    """Get simplified voice configuration (same for all emotions)"""
    # Single voice configuration for all emotions
    voice_config = {
        "voice": settings.default_voice,
        "stability": settings.voice_stability,
        "similarity_boost": settings.voice_similarity_boost,
        "style": settings.voice_style
    }
    
    # Return same configuration for all emotions
    return {
        "happy": voice_config,
        "sad": voice_config,
        "angry": voice_config,
        "fear": voice_config,
        "surprise": voice_config,
        "disgust": voice_config,
        "neutral": voice_config
    }


def validate_configuration() -> dict:
    """Validate configuration and return status"""
    status = {
        "elevenlabs_configured": bool(settings.elevenlabs_api_key),
        "openai_configured": bool(settings.openai_api_key),
        "database_configured": bool(settings.database_url),
        "redis_configured": bool(settings.redis_url)
    }
    
    return status


# Print configuration status on import
if __name__ == "__main__":
    config_status = validate_configuration()
    print("🔧 Configuration Status:")
    for key, value in config_status.items():
        status_icon = "✅" if value else "❌"
        print(f"   {status_icon} {key}: {value}")
