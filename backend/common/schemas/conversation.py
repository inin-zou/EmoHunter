"""
Conversation engine related Pydantic models
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from .base import BaseResponse


class ConversationMessage(BaseModel):
    """Individual conversation message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()
    emotion_context: Optional[str] = None


class ConversationRequest(BaseModel):
    """Request for conversation generation"""
    message: str
    emotion_context: Optional[str] = None
    conversation_history: Optional[List[ConversationMessage]] = None


class ConversationResponse(BaseResponse):
    """Response from conversation engine"""
    response_text: str
    conversation_id: Optional[str] = None
    emotion_adapted: bool = False


class TalkRequest(BaseModel):
    """Request for text-to-speech conversion"""
    text: str
    emotion: Optional[str] = "neutral"
    voice_settings: Optional[Dict[str, Any]] = None


class TalkResponse(BaseResponse):
    """Response with audio data"""
    audio_data: Optional[str] = None  # Base64 encoded audio
    audio_format: str = "mp3"
    duration_seconds: Optional[float] = None
