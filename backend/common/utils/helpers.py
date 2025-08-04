"""
Helper utilities shared across services
"""

import base64
import json
from typing import Dict, Any, Optional
from datetime import datetime


def encode_audio_to_base64(audio_bytes: bytes) -> str:
    """Encode audio bytes to base64 string"""
    return base64.b64encode(audio_bytes).decode('utf-8')


def decode_base64_to_audio(base64_string: str) -> bytes:
    """Decode base64 string to audio bytes"""
    return base64.b64decode(base64_string)


def create_response_dict(success: bool = True, message: str = None, data: Any = None) -> Dict[str, Any]:
    """Create standardized response dictionary"""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if message:
        response["message"] = message
    
    if data is not None:
        response["data"] = data
    
    return response


def validate_emotion(emotion: str) -> bool:
    """Validate if emotion is in supported list"""
    supported_emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "neutral"]
    return emotion.lower() in supported_emotions


def format_emotion_confidence(confidence: float) -> str:
    """Format confidence as percentage string"""
    return f"{confidence * 100:.1f}%"
