"""
Emotion analysis related Pydantic models
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from .base import BaseResponse


class EmotionData(BaseModel):
    """Individual emotion detection result"""
    emotion: str
    confidence: float
    timestamp: datetime = datetime.now()
    face_coordinates: Optional[Dict[str, int]] = None


class EmotionResponse(BaseResponse):
    """Response for emotion detection"""
    emotion_data: Optional[EmotionData] = None
    is_stable: bool = False
    history: Optional[List[EmotionData]] = None


class EmotionStreamRequest(BaseModel):
    """Request to start emotion stream"""
    camera_index: Optional[int] = 0
    update_interval: Optional[float] = 1.0


class EmotionStreamResponse(BaseResponse):
    """Response for emotion stream status"""
    stream_active: bool
    camera_index: int
    update_interval: float
