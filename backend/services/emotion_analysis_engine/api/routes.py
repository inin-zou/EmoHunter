"""
🎭 Emotion Analysis Engine API Routes

FastAPI routes for emotion detection and streaming functionality.
"""

import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import json
from typing import Optional

from common.schemas.emotion import EmotionResponse, EmotionStreamRequest, EmotionStreamResponse
from common.schemas.base import HealthResponse
from common.utils.logger import get_service_logger
from ..services.emotion_detector import EmotionDetector

logger = get_service_logger("emotion_api")
router = APIRouter()

# Global emotion detector instance
emotion_detector = EmotionDetector()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        service_name="Emotion Analysis Engine",
        version="1.0.0",
        status="healthy"
    )


@router.get("/current_emotion", response_model=EmotionResponse)
async def get_current_emotion():
    """Get the current detected emotion"""
    try:
        emotion_data = emotion_detector.get_current_emotion()
        history = emotion_detector.get_emotion_history()
        
        return EmotionResponse(
            emotion_data=emotion_data,
            is_stable=emotion_detector.emotion_stability_count >= 2,
            history=history,
            message=f"Current emotion: {emotion_data.emotion}"
        )
    except Exception as e:
        logger.error(f"❌ Error getting current emotion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start_emotion_stream", response_model=EmotionStreamResponse)
async def start_emotion_stream(request: EmotionStreamRequest):
    """Start emotion detection stream"""
    try:
        camera_index = request.camera_index or 0
        update_interval = request.update_interval or 1.0
        
        success = emotion_detector.start_camera_stream(camera_index)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to start camera stream")
        
        return EmotionStreamResponse(
            stream_active=True,
            camera_index=camera_index,
            update_interval=update_interval,
            message="Emotion stream started successfully"
        )
    except Exception as e:
        logger.error(f"❌ Error starting emotion stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop_emotion_stream", response_model=EmotionStreamResponse)
async def stop_emotion_stream():
    """Stop emotion detection stream"""
    try:
        emotion_detector.stop_camera_stream()
        
        return EmotionStreamResponse(
            stream_active=False,
            camera_index=0,
            update_interval=0.0,
            message="Emotion stream stopped successfully"
        )
    except Exception as e:
        logger.error(f"❌ Error stopping emotion stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream")
async def emotion_stream():
    """Server-sent events stream for real-time emotion updates"""
    
    async def generate_emotion_events():
        """Generate emotion events for streaming"""
        while emotion_detector.is_streaming:
            try:
                # Capture and analyze current frame
                emotion_data = emotion_detector.capture_and_analyze()
                
                if emotion_data:
                    # Create response data
                    response_data = {
                        "emotion": emotion_data.emotion,
                        "confidence": emotion_data.confidence,
                        "timestamp": emotion_data.timestamp.isoformat(),
                        "is_stable": emotion_detector.emotion_stability_count >= 2
                    }
                    
                    # Send as server-sent event
                    yield f"data: {json.dumps(response_data)}\n\n"
                
                # Wait for next update
                await asyncio.sleep(1.0)  # 1 second interval
                
            except Exception as e:
                logger.error(f"❌ Error in emotion stream: {e}")
                error_data = {
                    "error": str(e),
                    "timestamp": emotion_data.timestamp.isoformat() if 'emotion_data' in locals() else None
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                break
    
    return StreamingResponse(
        generate_emotion_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/reset")
async def reset_emotion_state():
    """Reset emotion detection state"""
    try:
        emotion_detector.reset_state()
        return {"success": True, "message": "Emotion state reset successfully"}
    except Exception as e:
        logger.error(f"❌ Error resetting emotion state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Get emotion detector status"""
    try:
        status = emotion_detector.get_status()
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"❌ Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
