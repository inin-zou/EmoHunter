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
from common.schemas.biometric import BiometricAnalysisResult
from common.utils.logger import get_service_logger
from ..services.emotion_detector import EmotionDetector
from ..services.biometric_processor import BiometricEmotionProcessor

logger = get_service_logger("emotion_api")
router = APIRouter()

# Global emotion detector instance
emotion_detector = EmotionDetector()

# Global biometric processor instance
biometric_processor = BiometricEmotionProcessor()

# Import biometric analysis store from biometric_routes
from .biometric_routes import analysis_results_store as biometric_analysis_store


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        service_name="Emotion Analysis Engine",
        version="1.0.0",
        status="healthy"
    )


@router.get("/current_emotion", response_model=EmotionResponse)
async def get_current_emotion(user_id: Optional[str] = None):
    """Get the current detected emotion with optional biometric context"""
    try:
        emotion_data = emotion_detector.get_current_emotion()
        history = emotion_detector.get_emotion_history()
        
        # Add biometric context if available
        biometric_context = None
        if user_id and user_id in biometric_analysis_store:
            biometric_analysis = biometric_analysis_store[user_id]
            biometric_context = biometric_processor.generate_contextual_prompt(biometric_analysis.insights)
        
        return EmotionResponse(
            emotion_data=emotion_data,
            is_stable=emotion_detector.emotion_stability_count >= 2,
            history=history,
            message=f"Current emotion: {emotion_data.emotion}",
            biometric_context=biometric_context
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


@router.get("/integrated_analysis/{user_id}")
async def get_integrated_emotion_analysis(user_id: str):
    """
    Get integrated emotion analysis combining facial detection and biometric data
    
    This endpoint provides a comprehensive emotional state assessment by combining:
    - Real-time facial emotion detection
    - Biometric data analysis (heart rate, HRV, sleep, activity)
    - CBT/DBT-based insights and recommendations
    """
    try:
        # Get current facial emotion
        facial_emotion = emotion_detector.get_current_emotion()
        facial_history = emotion_detector.get_emotion_history()
        
        # Get biometric analysis if available
        biometric_analysis = None
        biometric_context = None
        combined_confidence = facial_emotion.confidence
        
        if user_id in biometric_analysis_store:
            biometric_analysis = biometric_analysis_store[user_id]
            biometric_context = biometric_processor.generate_contextual_prompt(biometric_analysis.insights)
            
            # Adjust confidence based on biometric correlation
            if biometric_analysis.insights:
                # If biometric data supports facial emotion, increase confidence
                supporting_insights = [
                    insight for insight in biometric_analysis.insights 
                    if insight.primary_emotion_indicator.lower() in facial_emotion.emotion.lower() or
                       facial_emotion.emotion.lower() in insight.primary_emotion_indicator.lower()
                ]
                
                if supporting_insights:
                    avg_biometric_confidence = sum(i.confidence for i in supporting_insights) / len(supporting_insights)
                    combined_confidence = min(0.95, (facial_emotion.confidence + avg_biometric_confidence) / 2)
        
        # Generate comprehensive recommendations
        recommendations = []
        if biometric_analysis:
            recommendations.extend(biometric_analysis.recommendations)
        
        # Add facial emotion specific recommendations
        if facial_emotion.emotion in ["sad", "angry", "fear"]:
            recommendations.extend(["Consider mindfulness techniques", "Practice deep breathing"])
        elif facial_emotion.emotion == "happy":
            recommendations.append("Great! Consider sharing your positive energy")
        
        return {
            "user_id": user_id,
            "timestamp": facial_emotion.timestamp.isoformat(),
            "facial_emotion": {
                "emotion": facial_emotion.emotion,
                "confidence": facial_emotion.confidence,
                "is_stable": emotion_detector.emotion_stability_count >= 2,
                "history": [{
                    "emotion": h.emotion,
                    "confidence": h.confidence,
                    "timestamp": h.timestamp.isoformat()
                } for h in facial_history]
            },
            "biometric_analysis": {
                "available": biometric_analysis is not None,
                "wellness_score": biometric_analysis.overall_wellness_score if biometric_analysis else None,
                "insights_count": len(biometric_analysis.insights) if biometric_analysis else 0,
                "last_analysis": biometric_analysis.analysis_timestamp.isoformat() if biometric_analysis else None,
                "context": biometric_context
            },
            "integrated_assessment": {
                "primary_emotion": facial_emotion.emotion,
                "combined_confidence": combined_confidence,
                "data_sources": ["facial_detection"] + (["biometric_data"] if biometric_analysis else []),
                "recommendations": list(set(recommendations)),  # Remove duplicates
                "intervention_priority": "high" if combined_confidence > 0.8 and facial_emotion.emotion in ["sad", "angry", "fear"] else "normal"
            },
            "contextual_prompt": _generate_conversation_context(
                facial_emotion.emotion, 
                combined_confidence, 
                biometric_context
            )
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting integrated emotion analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_conversation_context(emotion: str, confidence: float, biometric_context: Optional[str] = None) -> str:
    """
    Generate contextual prompt for conversation engine based on integrated analysis
    """
    context_parts = []
    
    # Add facial emotion context
    confidence_level = "high" if confidence > 0.8 else "moderate" if confidence > 0.6 else "low"
    context_parts.append(f"Facial analysis shows {emotion} emotion with {confidence_level} confidence ({confidence:.1%})")
    
    # Add biometric context if available
    if biometric_context:
        context_parts.append(biometric_context)
    
    # Add therapeutic guidance
    if emotion in ["sad", "angry", "fear"]:
        context_parts.append("User may benefit from supportive, gentle conversation and coping strategies")
    elif emotion == "happy":
        context_parts.append("User is in a positive state - good time for encouragement and goal-setting")
    elif emotion == "neutral":
        context_parts.append("User appears calm - opportunity for check-in and emotional exploration")
    
    return ". ".join(context_parts) + ". Please respond with appropriate emotional awareness and support."
