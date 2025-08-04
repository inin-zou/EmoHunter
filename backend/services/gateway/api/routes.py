"""
🌐 Gateway API Routes

Unified API gateway that aggregates all microservices for the frontend.
"""

import httpx
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any

from common.config import settings
from common.schemas.base import HealthResponse
from common.schemas.emotion import EmotionResponse, EmotionStreamRequest
from common.schemas.conversation import ConversationRequest, TalkRequest
from common.utils.logger import get_service_logger

logger = get_service_logger("gateway_api")
router = APIRouter()

# Service URLs
EMOTION_SERVICE_URL = f"http://localhost:{settings.emotion_analysis_port}/api/v1"
CONVERSATION_SERVICE_URL = f"http://localhost:{settings.conversation_engine_port}/api/v1"
INCENTIVE_SERVICE_URL = f"http://localhost:{settings.incentive_engine_port}/api/v1"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        service_name="API Gateway",
        version="1.0.0",
        status="healthy"
    )


@router.get("/services/health")
async def check_all_services():
    """Check health of all microservices"""
    services_status = {}
    
    services = {
        "emotion_analysis": f"{EMOTION_SERVICE_URL}/health",
        "conversation_engine": f"{CONVERSATION_SERVICE_URL}/health"
        # "incentive_engine": f"{INCENTIVE_SERVICE_URL}/health"  # Under development
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(url, timeout=5.0)
                services_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
            except Exception as e:
                services_status[service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
    
    return {
        "success": True,
        "data": services_status
    }


# Emotion Analysis Endpoints
@router.get("/emotion/current")
async def get_current_emotion():
    """Get current detected emotion"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EMOTION_SERVICE_URL}/current_emotion")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"❌ Error getting current emotion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emotion/start_stream")
async def start_emotion_stream(request: EmotionStreamRequest):
    """Start emotion detection stream"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EMOTION_SERVICE_URL}/start_emotion_stream",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"❌ Error starting emotion stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emotion/stop_stream")
async def stop_emotion_stream():
    """Stop emotion detection stream"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{EMOTION_SERVICE_URL}/stop_emotion_stream")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"❌ Error stopping emotion stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Conversation Engine Endpoints
@router.post("/conversation/generate")
async def generate_conversation(request: ConversationRequest):
    """Generate conversation response"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CONVERSATION_SERVICE_URL}/generate",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"❌ Error generating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation/talk")
async def text_to_speech(request: TalkRequest):
    """Convert text to speech"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CONVERSATION_SERVICE_URL}/talk",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"❌ Error in text-to-speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation/chat")
async def chat_with_voice(request: ConversationRequest):
    """Generate conversation and convert to speech"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CONVERSATION_SERVICE_URL}/chat",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"❌ Error in chat with voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Incentive Engine Endpoints (Placeholder - Under Development)
# Note: These endpoints are commented out as the incentive engine is being developed by another team member

# @router.post("/incentive/create_goal")
# async def create_goal(...):
#     """Create a new goal - TO BE IMPLEMENTED"""
#     raise HTTPException(status_code=501, detail="Incentive engine under development")

# @router.post("/incentive/check_goal")
# async def check_goal_progress(...):
#     """Check goal progress - TO BE IMPLEMENTED"""
#     raise HTTPException(status_code=501, detail="Incentive engine under development")

# @router.get("/incentive/goals/active")
# async def get_active_goals():
#     """Get active goals - TO BE IMPLEMENTED"""
#     raise HTTPException(status_code=501, detail="Incentive engine under development")

# @router.get("/incentive/balance/{user_id}")
# async def get_user_balance(user_id: str):
#     """Get user balance - TO BE IMPLEMENTED"""
#     raise HTTPException(status_code=501, detail="Incentive engine under development")


# Unified Endpoints (combining multiple services)
@router.post("/unified/emotion_chat")
async def emotion_aware_chat(message: str, user_id: Optional[str] = "default_user"):
    """Unified endpoint: Get emotion, generate response, and convert to speech"""
    try:
        results = {}
        
        async with httpx.AsyncClient() as client:
            # 1. Get current emotion
            emotion_response = await client.get(f"{EMOTION_SERVICE_URL}/current_emotion")
            emotion_data = emotion_response.json()
            results["emotion"] = emotion_data
            
            current_emotion = emotion_data.get("emotion_data", {}).get("emotion", "neutral")
            
            # 2. Generate conversation response
            conversation_request = {
                "message": message,
                "emotion_context": current_emotion
            }
            
            chat_response = await client.post(
                f"{CONVERSATION_SERVICE_URL}/chat",
                json=conversation_request
            )
            chat_data = chat_response.json()
            results["conversation"] = chat_data
            
            # Note: Goal updates removed - incentive engine under development
            results["goal_updates"] = "Incentive engine under development"
            
            return {
                "success": True,
                "data": results
            }
            
    except Exception as e:
        logger.error(f"❌ Error in unified emotion chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unified/dashboard/{user_id}")
async def get_user_dashboard(user_id: str):
    """Get unified dashboard data for user"""
    try:
        dashboard_data = {}
        
        async with httpx.AsyncClient() as client:
            # Get current emotion
            emotion_response = await client.get(f"{EMOTION_SERVICE_URL}/current_emotion")
            dashboard_data["current_emotion"] = emotion_response.json()
            
            # Note: Incentive engine data removed - under development
            dashboard_data["active_goals"] = "Incentive engine under development"
            dashboard_data["balance"] = "Incentive engine under development"
            dashboard_data["recent_transactions"] = "Incentive engine under development"
            
            return {
                "success": True,
                "data": dashboard_data
            }
            
    except Exception as e:
        logger.error(f"❌ Error getting user dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
